import re
from typing import Any

import polars as pl

from app.etl.schema import SemanticDataType, infer_schema
from app.quality.models import RuleEvaluationResult, ValidationRule
from app.quality.types import RuleSeverity, RuleType

DEFAULT_MAX_NULL_PERCENTAGE = 30.0
DEFAULT_MAX_DUPLICATE_RATIO = 0.10
DEFAULT_MAX_CATEGORICAL_CARDINALITY = 100
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def build_default_rules(dataframe: pl.DataFrame) -> list[ValidationRule]:
    schema = infer_schema(dataframe)
    rules: list[ValidationRule] = []

    rules.append(
        ValidationRule(
            rule_id="dataset_duplicate_check",
            rule_type=RuleType.DUPLICATE_CHECK,
            description="Dataset duplicate row ratio must remain below threshold",
            severity=RuleSeverity.CRITICAL,
            parameters={"max_duplicate_ratio": DEFAULT_MAX_DUPLICATE_RATIO},
        )
    )

    for column_schema in schema.columns:
        column_name = column_schema.name
        lowered = column_name.lower()

        rules.append(
            ValidationRule(
                rule_id=f"{column_name}_null_check",
                rule_type=RuleType.NULL_CHECK,
                column=column_name,
                description=f"Column '{column_name}' null percentage must be below threshold",
                severity=RuleSeverity.CRITICAL if lowered in {"id", "name"} else RuleSeverity.WARNING,
                parameters={"max_null_percentage": 0.0 if lowered == "id" else DEFAULT_MAX_NULL_PERCENTAGE},
            )
        )

        if column_schema.semantic_type == SemanticDataType.NUMERIC:
            rules.append(
                ValidationRule(
                    rule_id=f"{column_name}_data_type",
                    rule_type=RuleType.DATA_TYPE,
                    column=column_name,
                    description=f"Column '{column_name}' must contain numeric values",
                    severity=RuleSeverity.CRITICAL,
                    parameters={"expected_type": SemanticDataType.NUMERIC.value},
                )
            )

            if any(token in lowered for token in ("amount", "price", "quantity", "count", "id")):
                rules.append(
                    ValidationRule(
                        rule_id=f"{column_name}_range",
                        rule_type=RuleType.RANGE,
                        column=column_name,
                        description=f"Column '{column_name}' must be non-negative",
                        severity=RuleSeverity.CRITICAL,
                        parameters={"min_value": 0},
                    )
                )

        if column_schema.semantic_type == SemanticDataType.CATEGORICAL:
            rules.append(
                ValidationRule(
                    rule_id=f"{column_name}_categorical",
                    rule_type=RuleType.CATEGORICAL,
                    column=column_name,
                    description=f"Column '{column_name}' cardinality must remain within allowed limits",
                    severity=RuleSeverity.WARNING,
                    parameters={"max_unique_values": DEFAULT_MAX_CATEGORICAL_CARDINALITY},
                )
            )

            if any(token in lowered for token in ("email", "mail")):
                rules.append(
                    ValidationRule(
                        rule_id=f"{column_name}_regex",
                        rule_type=RuleType.REGEX,
                        column=column_name,
                        description=f"Column '{column_name}' values must match email pattern",
                        severity=RuleSeverity.CRITICAL,
                        parameters={"pattern": EMAIL_PATTERN.pattern},
                    )
                )

        if column_schema.semantic_type in {SemanticDataType.DATETIME, SemanticDataType.CATEGORICAL}:
            if any(token in lowered for token in ("date", "created", "updated", "timestamp")):
                rules.append(
                    ValidationRule(
                        rule_id=f"{column_name}_regex",
                        rule_type=RuleType.REGEX,
                        column=column_name,
                        description=f"Column '{column_name}' values must match ISO date pattern",
                        severity=RuleSeverity.WARNING,
                        parameters={"pattern": ISO_DATE_PATTERN.pattern},
                    )
                )

    return rules


def evaluate_rule(dataframe: pl.DataFrame, rule: ValidationRule) -> RuleEvaluationResult:
    evaluators = {
        RuleType.NULL_CHECK: _evaluate_null_check,
        RuleType.DUPLICATE_CHECK: _evaluate_duplicate_check,
        RuleType.DATA_TYPE: _evaluate_data_type,
        RuleType.RANGE: _evaluate_range,
        RuleType.REGEX: _evaluate_regex,
        RuleType.CATEGORICAL: _evaluate_categorical,
    }
    evaluator = evaluators[rule.rule_type]
    return evaluator(dataframe, rule)


def _evaluate_null_check(dataframe: pl.DataFrame, rule: ValidationRule) -> RuleEvaluationResult:
    column = rule.column or ""
    series = dataframe.get_column(column)
    row_count = dataframe.height
    null_count = int(series.null_count())
    if series.dtype in {pl.Utf8, pl.String, pl.Categorical}:
        null_count += sum(1 for value in series.to_list() if value == "")
    null_percentage = round((null_count / row_count) * 100, 4) if row_count else 0.0
    max_null_percentage = float(rule.parameters.get("max_null_percentage", DEFAULT_MAX_NULL_PERCENTAGE))
    passed = null_percentage <= max_null_percentage

    return RuleEvaluationResult(
        rule_id=rule.rule_id,
        rule_type=rule.rule_type,
        description=rule.description,
        passed=passed,
        message=(
            f"Null percentage {null_percentage}% is within limit {max_null_percentage}%"
            if passed
            else f"Null percentage {null_percentage}% exceeds limit {max_null_percentage}%"
        ),
        column=column,
        severity=rule.severity,
        details={
            "null_count": null_count,
            "null_percentage": null_percentage,
            "max_null_percentage": max_null_percentage,
        },
    )


def _evaluate_duplicate_check(dataframe: pl.DataFrame, rule: ValidationRule) -> RuleEvaluationResult:
    row_count = dataframe.height
    unique_rows = dataframe.unique(maintain_order=True).height
    duplicate_rows = max(row_count - unique_rows, 0)
    duplicate_ratio = round(duplicate_rows / row_count, 4) if row_count else 0.0
    max_duplicate_ratio = float(rule.parameters.get("max_duplicate_ratio", DEFAULT_MAX_DUPLICATE_RATIO))
    passed = duplicate_ratio <= max_duplicate_ratio

    return RuleEvaluationResult(
        rule_id=rule.rule_id,
        rule_type=rule.rule_type,
        description=rule.description,
        passed=passed,
        message=(
            f"Duplicate ratio {duplicate_ratio:.2%} is within limit {max_duplicate_ratio:.2%}"
            if passed
            else f"Duplicate ratio {duplicate_ratio:.2%} exceeds limit {max_duplicate_ratio:.2%}"
        ),
        severity=rule.severity,
        details={
            "duplicate_rows": duplicate_rows,
            "duplicate_ratio": duplicate_ratio,
            "max_duplicate_ratio": max_duplicate_ratio,
        },
    )


def _evaluate_data_type(dataframe: pl.DataFrame, rule: ValidationRule) -> RuleEvaluationResult:
    column = rule.column or ""
    schema = infer_schema(dataframe)
    column_schema = next((item for item in schema.columns if item.name == column), None)
    expected_type = rule.parameters.get("expected_type", SemanticDataType.NUMERIC.value)
    actual_type = column_schema.semantic_type.value if column_schema else "unknown"
    passed = actual_type == expected_type

    return RuleEvaluationResult(
        rule_id=rule.rule_id,
        rule_type=rule.rule_type,
        description=rule.description,
        passed=passed,
        message=(
            f"Column '{column}' has expected type '{expected_type}'"
            if passed
            else f"Column '{column}' has type '{actual_type}', expected '{expected_type}'"
        ),
        column=column,
        severity=rule.severity,
        details={"expected_type": expected_type, "actual_type": actual_type},
    )


def _evaluate_range(dataframe: pl.DataFrame, rule: ValidationRule) -> RuleEvaluationResult:
    column = rule.column or ""
    series = dataframe.get_column(column).cast(pl.Float64, strict=False)
    min_value = rule.parameters.get("min_value")
    max_value = rule.parameters.get("max_value")

    violations = 0
    for value in series.to_list():
        if value is None:
            continue
        numeric_value = float(value)
        if min_value is not None and numeric_value < float(min_value):
            violations += 1
        elif max_value is not None and numeric_value > float(max_value):
            violations += 1

    passed = violations == 0
    bounds = {key: value for key, value in {"min_value": min_value, "max_value": max_value}.items() if value is not None}

    return RuleEvaluationResult(
        rule_id=rule.rule_id,
        rule_type=rule.rule_type,
        description=rule.description,
        passed=passed,
        message=(
            f"All values in '{column}' are within configured range"
            if passed
            else f"{violations} value(s) in '{column}' are outside configured range"
        ),
        column=column,
        severity=rule.severity,
        details={"violations": violations, **bounds},
    )


def _evaluate_regex(dataframe: pl.DataFrame, rule: ValidationRule) -> RuleEvaluationResult:
    column = rule.column or ""
    pattern = re.compile(str(rule.parameters.get("pattern", "")))
    series = dataframe.get_column(column).cast(pl.Utf8, strict=False).drop_nulls()
    invalid_count = 0

    for value in series.to_list():
        if value is None or not pattern.match(str(value)):
            invalid_count += 1

    passed = invalid_count == 0

    return RuleEvaluationResult(
        rule_id=rule.rule_id,
        rule_type=rule.rule_type,
        description=rule.description,
        passed=passed,
        message=(
            f"All non-null values in '{column}' match pattern"
            if passed
            else f"{invalid_count} value(s) in '{column}' failed regex validation"
        ),
        column=column,
        severity=rule.severity,
        details={
            "pattern": pattern.pattern,
            "invalid_count": invalid_count,
            "checked_values": int(series.len()),
        },
    )


def _evaluate_categorical(dataframe: pl.DataFrame, rule: ValidationRule) -> RuleEvaluationResult:
    column = rule.column or ""
    series = dataframe.get_column(column)
    unique_count = int(series.n_unique())
    max_unique_values = int(rule.parameters.get("max_unique_values", DEFAULT_MAX_CATEGORICAL_CARDINALITY))
    allowed_values = rule.parameters.get("allowed_values")

    passed = unique_count <= max_unique_values
    invalid_values: list[str] = []

    if allowed_values:
        allowed_set = {str(value) for value in allowed_values}
        observed = {str(value) for value in series.drop_nulls().to_list()}
        invalid_values = sorted(observed - allowed_set)
        passed = passed and not invalid_values

    return RuleEvaluationResult(
        rule_id=rule.rule_id,
        rule_type=rule.rule_type,
        description=rule.description,
        passed=passed,
        message=(
            f"Column '{column}' passed categorical validation"
            if passed
            else f"Column '{column}' failed categorical validation"
        ),
        column=column,
        severity=rule.severity,
        details={
            "unique_count": unique_count,
            "max_unique_values": max_unique_values,
            "invalid_values": invalid_values,
        },
    )
