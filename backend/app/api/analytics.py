from fastapi import APIRouter, Depends, status

from app.schemas.analytics import AnalyticsRequest, AnalyticsResponse
from app.services.analytics_service import AnalyticsService, get_analytics_service

router = APIRouter(tags=["Analytics"])


@router.post(
    "/analytics",
    response_model=AnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze an uploaded dataset",
    description=(
        "Read an uploaded CSV, Excel (.xlsx), or JSON file and return "
        "dataset analytics including statistics, correlations, outliers, "
        "and categorical and datetime summaries."
    ),
    responses={
        404: {"description": "Uploaded file not found"},
        400: {"description": "Unsupported or invalid dataset format"},
        500: {"description": "Analytics computation failed"},
    },
)
async def analyze_dataset(
    request: AnalyticsRequest,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsResponse:
    return analytics_service.analyze_uploaded_file(request.stored_filename)
