from pathlib import Path

import polars as pl
import pytest

from app.quality.engine import QualityValidationEngine
from app.quality.rules import build_default_rules, evaluate_rule
from app.quality.scorer import calculate_quality_score
from app.etl.reader import DatasetReader
from app.quality.models import RuleEvaluationResult, ValidationRule
from app.quality.types import RuleSeverity, RuleType

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe():
    reader = DatasetReader()
    dataframe, _ = reader.read(FIXTURES_DIR / "sample.csv")
    return dataframe


def test_build_default_rules_includes_required_types(sample_dataframe):
    rules = build_default_rules(sample_dataframe)
    rule_types = {rule.rule_type for rule in rules}

    assert RuleType.NULL_CHECK in rule_types
    assert RuleType.DUPLICATE_CHECK in rule_types
    assert RuleType.DATA_TYPE in rule_types
    assert RuleType.RANGE in rule_types
    assert RuleType.REGEX in rule_types
    assert RuleType.CATEGORICAL in rule_types


def test_quality_engine_returns_summary(sample_dataframe):
    engine = QualityValidationEngine()
    result = engine.validate(sample_dataframe)

    assert result["validation_summary"]["total_rules"] > 0
    assert (
        result["validation_summary"]["passed_rules"]
        + result["validation_summary"]["failed_rules"]
        == result["validation_summary"]["total_rules"]
    )
    assert 0 <= result["validation_summary"]["quality_score"] <= 100
    assert "validation_report" in result


def test_duplicate_rule_fails_for_sample_csv(sample_dataframe):
    rules = build_default_rules(sample_dataframe)
    duplicate_rule = next(rule for rule in rules if rule.rule_type == RuleType.DUPLICATE_CHECK)
    result = evaluate_rule(sample_dataframe, duplicate_rule)

    assert result.passed is False
    assert result.details["duplicate_rows"] == 1


def test_null_check_rule_for_name_column(sample_dataframe):
    rule = ValidationRule(
        rule_id="name_null_check",
        rule_type=RuleType.NULL_CHECK,
        column="name",
        description="Name null check",
        parameters={"max_null_percentage": 30.0},
    )
    result = evaluate_rule(sample_dataframe, rule)

    assert result.passed is True
    assert result.details["null_count"] == 1


def test_quality_score_weighting():
    evaluations = [
        RuleEvaluationResult(
            rule_id="critical_pass",
            rule_type=RuleType.NULL_CHECK,
            description="pass",
            passed=True,
            message="ok",
            severity=RuleSeverity.CRITICAL,
        ),
        RuleEvaluationResult(
            rule_id="critical_fail",
            rule_type=RuleType.DUPLICATE_CHECK,
            description="fail",
            passed=False,
            message="bad",
            severity=RuleSeverity.CRITICAL,
        ),
    ]

    score = calculate_quality_score(evaluations)
    assert score == 50.0
