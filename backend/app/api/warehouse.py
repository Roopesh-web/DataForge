from fastapi import APIRouter, Depends, Query, status

from app.schemas.warehouse import (
    WarehouseHistoryResponse,
    WarehouseLoadRequest,
    WarehouseLoadResponse,
)
from app.services.warehouse_service import WarehouseService, get_warehouse_service
from app.utils.exceptions import AppException, ErrorCode
from app.warehouse.exceptions import WarehouseLoadError

router = APIRouter(tags=["Warehouse"])


@router.post(
    "/warehouse/load",
    response_model=WarehouseLoadResponse,
    status_code=status.HTTP_200_OK,
    summary="Load dataset into PostgreSQL warehouse",
    description=(
        "Load a validated uploaded dataset into the enterprise warehouse using "
        "transactional batch inserts and automatic table creation."
    ),
    responses={
        404: {"description": "Uploaded file not found"},
        400: {"description": "Invalid stored filename"},
        500: {"description": "Warehouse load failed"},
    },
)
async def load_dataset_to_warehouse(
    request: WarehouseLoadRequest,
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseLoadResponse:
    try:
        return warehouse_service.load_uploaded_file(request.stored_filename)
    except WarehouseLoadError as exc:
        raise AppException(
            message=exc.message,
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR,
        ) from exc


@router.get(
    "/warehouse/history",
    response_model=WarehouseHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get warehouse load history",
    description="Returns recent warehouse load operations for dashboard and audit use.",
)
async def get_warehouse_history(
    limit: int = Query(default=50, ge=1, le=500),
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
) -> WarehouseHistoryResponse:
    return warehouse_service.get_load_history(limit=limit)
