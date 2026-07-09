from datetime import datetime

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str = Field(..., description="Saved filename on disk")
    size: int = Field(..., description="File size in bytes", ge=0)
    type: str = Field(..., description="Detected file type")
    timestamp: datetime = Field(..., description="Upload timestamp in UTC")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "sales_data_20260709.csv",
                "size": 1048576,
                "type": "csv",
                "timestamp": "2026-07-09T12:00:00Z",
            }
        }
    }
