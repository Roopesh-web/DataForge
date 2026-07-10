from enum import Enum
from pathlib import Path

import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.json as pa_json

from app.core.logging import get_logger
from app.etl.exceptions import UnsupportedDatasetFormatError

logger = get_logger("etl.reader")


class DatasetFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


EXTENSION_FORMAT_MAP: dict[str, DatasetFormat] = {
    ".csv": DatasetFormat.CSV,
    ".xlsx": DatasetFormat.EXCEL,
    ".json": DatasetFormat.JSON,
}


def detect_file_format(file_path: Path) -> DatasetFormat:
    extension = file_path.suffix.lower()
    detected = EXTENSION_FORMAT_MAP.get(extension)

    if detected is None:
        raise UnsupportedDatasetFormatError(stored_filename=file_path.name)

    logger.info(
        "File format detected | file={} | format={}",
        file_path.name,
        detected.value,
    )
    return detected


class DatasetReader:
    def read(self, file_path: Path) -> tuple[pl.DataFrame, DatasetFormat]:
        if not file_path.exists():
            raise FileNotFoundError(str(file_path))

        file_format = detect_file_format(file_path)

        logger.info(
            "Reading dataset | file={} | format={}",
            file_path.name,
            file_format.value,
        )

        if file_format == DatasetFormat.CSV:
            dataframe = self._read_csv(file_path)
        elif file_format == DatasetFormat.EXCEL:
            dataframe = self._read_excel(file_path)
        else:
            dataframe = self._read_json(file_path)

        logger.info(
            "Dataset loaded | file={} | rows={} | columns={}",
            file_path.name,
            dataframe.height,
            dataframe.width,
        )

        return dataframe, file_format

    def _read_csv(self, file_path: Path) -> pl.DataFrame:
        try:
            arrow_table = pa_csv.read_csv(file_path)
            return pl.from_arrow(arrow_table)
        except Exception:
            return pl.read_csv(file_path)

    def _read_excel(self, file_path: Path) -> pl.DataFrame:
        pandas_frame = pd.read_excel(file_path, engine="openpyxl")
        arrow_table = pa.Table.from_pandas(pandas_frame, preserve_index=False)
        return pl.from_arrow(arrow_table)

    def _read_json(self, file_path: Path) -> pl.DataFrame:
        try:
            arrow_table = pa_json.read_json(file_path)
            return pl.from_arrow(arrow_table)
        except Exception:
            pandas_frame = pd.read_json(file_path)
            if isinstance(pandas_frame, pd.Series):
                pandas_frame = pandas_frame.to_frame()
            arrow_table = pa.Table.from_pandas(pandas_frame, preserve_index=False)
            return pl.from_arrow(arrow_table)

    @staticmethod
    def memory_usage_bytes(dataframe: pl.DataFrame) -> int:
        arrow_table = dataframe.to_arrow()
        return int(arrow_table.nbytes)
