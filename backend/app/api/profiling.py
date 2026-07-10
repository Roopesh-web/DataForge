from fastapi import APIRouter, Depends, status

from app.schemas.profiling import ProfilingRequest, ProfilingResponse
from app.services.profiling_service import ProfilingService, get_profiling_service

router = APIRouter(tags=["Profiling"])


@router.post(
    "/profile",
    response_model=ProfilingResponse,
    status_code=status.HTTP_200_OK,
    summary="Profile an uploaded dataset",
    description=(
        "Read an uploaded CSV, Excel (.xlsx), or JSON file and return "
        "schema inference, column statistics, and dataset-level metrics."
    ),
    responses={
        404: {"description": "Uploaded file not found"},
        400: {"description": "Unsupported or invalid dataset format"},
        500: {"description": "Profiling failed"},
    },
)
async def profile_dataset(
    request: ProfilingRequest,
    profiling_service: ProfilingService = Depends(get_profiling_service),
) -> ProfilingResponse:
    return profiling_service.profile_uploaded_file(request.stored_filename)
