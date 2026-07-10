from enum import Enum


class RuleType(str, Enum):
    NULL_CHECK = "null_check"
    DUPLICATE_CHECK = "duplicate_check"
    DATA_TYPE = "data_type"
    RANGE = "range"
    REGEX = "regex"
    CATEGORICAL = "categorical"


class RuleSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
