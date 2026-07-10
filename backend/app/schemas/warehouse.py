from datetime import datetime

from pydantic import BaseModel, Field


class WarehouseLoadRequest(BaseModel):
    stored_filename: str = Field(
        ...,
        min_length=1,
        description="Stored filename returned by the upload API",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv"],
    )


class WarehouseLoadResponse(BaseModel):
    status: str = Field(..., examples=["success"])
    table_name: str
    rows_loaded: int = Field(..., ge=0)
    duration_ms: int = Field(..., ge=0)


class WarehouseLoadHistoryItem(BaseModel):
    id: int
    stored_filename: str
    table_name: str
    rows_loaded: int
    status: str
    duration_ms: int
    timestamp: datetime
    error_message: str | None = None


class WarehouseHistoryResponse(BaseModel):
    loads: list[WarehouseLoadHistoryItem] = Field(default_factory=list)
