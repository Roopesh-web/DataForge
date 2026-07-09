from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: str | None = Field(default=None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: str | None = Field(default=None, description="Machine-readable error code")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: list[ErrorDetail] | None = Field(
        default=None,
        description="Additional error details",
    )
    request_id: str | None = Field(default=None, description="Request correlation ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "file",
                        "message": "File type not supported",
                        "code": "INVALID_FILE_TYPE",
                    }
                ],
                "request_id": "abc-123",
            }
        }
    }


class MessageResponse(BaseModel):
    message: str
    data: dict[str, Any] | None = None
