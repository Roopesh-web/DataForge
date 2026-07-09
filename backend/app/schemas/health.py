from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(
        default="healthy",
        examples=["healthy"],
        description="Application health status",
    )

    model_config = {"json_schema_extra": {"example": {"status": "healthy"}}}
