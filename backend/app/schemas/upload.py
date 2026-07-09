from datetime import datetime

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    original_filename: str = Field(..., description="Original filename provided by the client")
    stored_filename: str = Field(..., description="Unique filename stored on disk")
    timestamp: datetime = Field(..., description="Upload timestamp in UTC")
    size: int = Field(..., description="File size in bytes", ge=0)
    file_type: str = Field(..., description="Detected file type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "original_filename": "sales_data.csv",
                "stored_filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv",
                "timestamp": "2026-07-09T12:00:00Z",
                "size": 1048576,
                "file_type": "csv",
            }
        }
    }
