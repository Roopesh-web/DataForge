from fastapi import APIRouter, Depends, File, UploadFile, status

from app.schemas.upload import UploadResponse
from app.services.upload_service import UploadService, get_upload_service

router = APIRouter(tags=["Upload"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a data file",
    description=(
        "Upload a CSV, Excel, or JSON file. "
        f"Maximum file size is configurable (default 100 MB)."
    ),
    responses={
        400: {"description": "Invalid file type or empty file"},
        413: {"description": "File size exceeds maximum allowed limit"},
        500: {"description": "Failed to save uploaded file"},
    },
)
async def upload_file(
    file: UploadFile = File(..., description="CSV, Excel (.xlsx/.xls), or JSON file"),
    upload_service: UploadService = Depends(get_upload_service),
) -> UploadResponse:
    return await upload_service.process_upload(file)
