import time
from pathlib import Path

import polars as pl
from sqlalchemy import inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import SessionLocal, engine as default_engine
from app.etl.exceptions import ProfilingError, ProfilingFileNotFoundError
from app.etl.reader import DatasetReader
from app.models.warehouse import DatasetMetadata, UploadHistory, WarehouseLoadHistory
from app.quality.engine import QualityValidationEngine
from app.schemas.warehouse import (
    WarehouseHistoryResponse,
    WarehouseLoadHistoryItem,
    WarehouseLoadResponse,
)
from app.utils.exceptions import AppException, ErrorCode
from app.warehouse.db_init import ensure_metadata_tables
from app.warehouse.exceptions import WarehouseLoadError, build_warehouse_table_name
from app.warehouse.loader import batch_insert_dataframe
from app.warehouse.table_manager import WAREHOUSE_METADATA, ensure_warehouse_table

logger = get_logger("services.warehouse")


class WarehouseService:
    def __init__(
        self,
        upload_dir: Path | None = None,
        reader: DatasetReader | None = None,
        quality_engine: QualityValidationEngine | None = None,
        session_factory: sessionmaker | None = None,
        db_engine: Engine | None = None,
    ) -> None:
        self.upload_dir = upload_dir or settings.upload_path
        self.reader = reader or DatasetReader()
        self.quality_engine = quality_engine or QualityValidationEngine()
        self.session_factory = session_factory or SessionLocal
        self.engine = db_engine or default_engine
        ensure_metadata_tables(self.engine)

    def load_uploaded_file(self, stored_filename: str) -> WarehouseLoadResponse:
        logger.info("Warehouse load started | stored_filename={}", stored_filename)
        start_time = time.perf_counter()

        try:
            file_path = self._resolve_file_path(stored_filename)
            dataframe, file_format = self.reader.read(file_path)
            quality_result = self.quality_engine.validate(dataframe)
            quality_score = quality_result["validation_summary"]["quality_score"]
            table_name = build_warehouse_table_name(stored_filename)
            filename = self._resolve_original_filename(stored_filename)

            rows_loaded = 0
            with self.session_factory() as session:
                try:
                    with session.begin():
                        self._clear_existing_warehouse_rows(
                            session=session,
                            stored_filename=stored_filename,
                            table_name=table_name,
                            dataframe=dataframe,
                        )
                        rows_loaded = batch_insert_dataframe(
                            session=session,
                            engine=self.engine,
                            table_name=table_name,
                            dataframe=dataframe,
                        )
                        self._upsert_upload_history(
                            session=session,
                            filename=filename,
                            stored_filename=stored_filename,
                            file_type=file_format.value,
                            size_bytes=file_path.stat().st_size,
                        )
                        self._upsert_dataset_metadata(
                            session=session,
                            filename=filename,
                            stored_filename=stored_filename,
                            row_count=dataframe.height,
                            column_count=dataframe.width,
                            quality_score=quality_score,
                            warehouse_table=table_name,
                        )
                        self._record_load_history(
                            session=session,
                            stored_filename=stored_filename,
                            warehouse_table=table_name,
                            rows_loaded=rows_loaded,
                            status="success",
                            duration_ms=self._elapsed_ms(start_time),
                        )
                except Exception as exc:
                    self._record_failed_load(
                        stored_filename=stored_filename,
                        warehouse_table=table_name,
                        duration_ms=self._elapsed_ms(start_time),
                        error_message=str(exc),
                    )
                    raise WarehouseLoadError(f"Warehouse load transaction failed: {exc}") from exc

            duration_ms = self._elapsed_ms(start_time)
            logger.info(
                "Warehouse load completed | stored_filename={} | table={} | rows={} | duration_ms={}",
                stored_filename,
                table_name,
                rows_loaded,
                duration_ms,
            )

            return WarehouseLoadResponse(
                status="success",
                table_name=table_name,
                rows_loaded=rows_loaded,
                duration_ms=duration_ms,
            )

        except AppException:
            raise
        except WarehouseLoadError:
            raise
        except Exception as exc:
            logger.error(
                "Warehouse load failed | stored_filename={} | error={}",
                stored_filename,
                str(exc),
            )
            raise ProfilingError(
                message=f"Failed to load dataset into warehouse: {exc}",
                status_code=500,
                error_code=ErrorCode.INTERNAL_ERROR,
            ) from exc

    def get_load_history(self, limit: int = 50) -> WarehouseHistoryResponse:
        ensure_metadata_tables(self.engine)
        try:
            with self.session_factory() as session:
                records = session.scalars(
                    select(WarehouseLoadHistory)
                    .order_by(WarehouseLoadHistory.created_at.desc())
                    .limit(limit)
                ).all()
        except SQLAlchemyError as exc:
            logger.warning("Failed to fetch warehouse load history: {}", exc)
            return WarehouseHistoryResponse(loads=[])

        loads = [
            WarehouseLoadHistoryItem(
                id=record.id,
                stored_filename=record.stored_filename,
                table_name=record.warehouse_table,
                rows_loaded=record.rows_loaded,
                status=record.status,
                duration_ms=record.duration_ms,
                timestamp=record.loaded_at,
                error_message=record.error_message,
            )
            for record in records
        ]
        return WarehouseHistoryResponse(loads=loads)

    def _clear_existing_warehouse_rows(
        self,
        session: Session,
        stored_filename: str,
        table_name: str,
        dataframe: pl.DataFrame,
    ) -> None:
        existing_metadata = session.scalar(
            select(DatasetMetadata).where(DatasetMetadata.stored_filename == stored_filename)
        )
        if not existing_metadata:
            return

        inspector = inspect(self.engine)
        if not inspector.has_table(table_name):
            return

        table = ensure_warehouse_table(self.engine, table_name, dataframe)
        session.execute(table.delete())

    def _resolve_file_path(self, stored_filename: str) -> Path:
        safe_name = Path(stored_filename).name
        if safe_name != stored_filename:
            raise ProfilingError(
                message="Invalid stored filename",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR,
            )

        file_path = self.upload_dir / safe_name
        if not file_path.exists():
            raise ProfilingFileNotFoundError(stored_filename=safe_name)

        return file_path

    def _resolve_original_filename(self, stored_filename: str) -> str:
        with self.session_factory() as session:
            existing = session.scalar(
                select(UploadHistory).where(UploadHistory.stored_filename == stored_filename)
            )
            if existing:
                return existing.filename
        return stored_filename

    def _upsert_upload_history(
        self,
        session: Session,
        filename: str,
        stored_filename: str,
        file_type: str,
        size_bytes: int,
    ) -> None:
        existing = session.scalar(
            select(UploadHistory).where(UploadHistory.stored_filename == stored_filename)
        )
        if existing:
            existing.filename = filename
            existing.file_type = file_type
            existing.size_bytes = size_bytes
            return

        session.add(
            UploadHistory(
                filename=filename,
                stored_filename=stored_filename,
                file_type=file_type,
                size_bytes=size_bytes,
            )
        )

    def _upsert_dataset_metadata(
        self,
        session: Session,
        filename: str,
        stored_filename: str,
        row_count: int,
        column_count: int,
        quality_score: float,
        warehouse_table: str,
    ) -> None:
        existing = session.scalar(
            select(DatasetMetadata).where(DatasetMetadata.stored_filename == stored_filename)
        )
        if existing:
            existing.filename = filename
            existing.row_count = row_count
            existing.column_count = column_count
            existing.quality_score = quality_score
            existing.warehouse_table = warehouse_table
            return

        session.add(
            DatasetMetadata(
                filename=filename,
                stored_filename=stored_filename,
                row_count=row_count,
                column_count=column_count,
                quality_score=quality_score,
                warehouse_table=warehouse_table,
            )
        )

    def _record_load_history(
        self,
        session: Session,
        stored_filename: str,
        warehouse_table: str,
        rows_loaded: int,
        status: str,
        duration_ms: int,
        error_message: str | None = None,
    ) -> None:
        session.add(
            WarehouseLoadHistory(
                stored_filename=stored_filename,
                warehouse_table=warehouse_table,
                rows_loaded=rows_loaded,
                status=status,
                duration_ms=duration_ms,
                error_message=error_message,
            )
        )

    def _record_failed_load(
        self,
        stored_filename: str,
        warehouse_table: str,
        duration_ms: int,
        error_message: str,
    ) -> None:
        try:
            with self.session_factory() as session:
                with session.begin():
                    self._record_load_history(
                        session=session,
                        stored_filename=stored_filename,
                        warehouse_table=warehouse_table,
                        rows_loaded=0,
                        status="failed",
                        duration_ms=duration_ms,
                        error_message=error_message,
                    )
        except Exception as exc:
            logger.error("Failed to record warehouse load failure: {}", exc)

    @staticmethod
    def _elapsed_ms(start_time: float) -> int:
        return int((time.perf_counter() - start_time) * 1000)


def get_warehouse_service() -> WarehouseService:
    return WarehouseService()
