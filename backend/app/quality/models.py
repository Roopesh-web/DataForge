from dataclasses import dataclass, field
from typing import Any

from app.quality.types import RuleSeverity, RuleType


@dataclass
class ValidationRule:
    rule_id: str
    rule_type: RuleType
    description: str
    column: str | None = None
    severity: RuleSeverity = RuleSeverity.WARNING
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleEvaluationResult:
    rule_id: str
    rule_type: RuleType
    description: str
    passed: bool
    message: str
    column: str | None = None
    severity: RuleSeverity = RuleSeverity.WARNING
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type.value,
            "description": self.description,
            "passed": self.passed,
            "message": self.message,
            "column": self.column,
            "severity": self.severity.value,
            "details": self.details,
        }
