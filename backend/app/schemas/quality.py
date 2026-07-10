from pydantic import BaseModel, Field


class QualityCheckRequest(BaseModel):
    stored_filename: str = Field(
        ...,
        min_length=1,
        description="Stored filename returned by the upload API",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv"],
    )


class ValidationSummary(BaseModel):
    total_rules: int = Field(..., ge=0)
    passed_rules: int = Field(..., ge=0)
    failed_rules: int = Field(..., ge=0)
    quality_score: float = Field(..., ge=0, le=100)


class ValidationRuleResult(BaseModel):
    rule_id: str
    rule_type: str
    description: str
    passed: bool
    message: str
    column: str | None = None
    severity: str = "warning"
    details: dict = Field(default_factory=dict)


class QualityCheckResponse(BaseModel):
    stored_filename: str
    validation_summary: ValidationSummary
    passed_rules: list[ValidationRuleResult] = Field(default_factory=list)
    failed_rules: list[ValidationRuleResult] = Field(default_factory=list)
    validation_report: dict = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "stored_filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.csv",
                "validation_summary": {
                    "total_rules": 12,
                    "passed_rules": 10,
                    "failed_rules": 2,
                    "quality_score": 83.33,
                },
                "passed_rules": [],
                "failed_rules": [],
                "validation_report": {
                    "dataset_rows": 1000,
                    "dataset_columns": 8,
                    "rule_types_evaluated": ["null_check", "duplicate_check"],
                },
            }
        }
    }
