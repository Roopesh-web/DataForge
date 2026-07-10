from fastapi import APIRouter, Depends, status

from app.schemas.quality import QualityCheckRequest, QualityCheckResponse
from app.services.quality_service import QualityService, get_quality_service

router = APIRouter(tags=["Data Quality"])


@router.post(
    "/quality-check",
    response_model=QualityCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Run enterprise data quality checks",
    description=(
        "Validate an uploaded dataset using reusable data quality rules including "
        "null checks, duplicate checks, data type validation, range validation, "
        "regex validation, and categorical validation."
    ),
    responses={
        404: {"description": "Uploaded file not found"},
        400: {"description": "Invalid dataset or filename"},
        500: {"description": "Quality validation failed"},
    },
)
async def quality_check(
    request: QualityCheckRequest,
    quality_service: QualityService = Depends(get_quality_service),
) -> QualityCheckResponse:
    return quality_service.check_uploaded_file(request.stored_filename)
