from typing import Any

import polars as pl

from app.core.logging import get_logger
from app.quality.models import RuleEvaluationResult, ValidationRule
from app.quality.rules import build_default_rules, evaluate_rule
from app.quality.scorer import calculate_quality_score

logger = get_logger("quality.engine")


class QualityValidationEngine:
    def validate(
        self,
        dataframe: pl.DataFrame,
        rules: list[ValidationRule] | None = None,
    ) -> dict[str, Any]:
        active_rules = rules or build_default_rules(dataframe)

        logger.info("Quality validation started | rules={}", len(active_rules))

        evaluations: list[RuleEvaluationResult] = []
        for rule in active_rules:
            logger.debug("Evaluating rule | rule_id={} | type={}", rule.rule_id, rule.rule_type.value)
            evaluations.append(evaluate_rule(dataframe, rule))

        passed_rules = [result for result in evaluations if result.passed]
        failed_rules = [result for result in evaluations if not result.passed]
        quality_score = calculate_quality_score(evaluations)

        summary = {
            "total_rules": len(evaluations),
            "passed_rules": len(passed_rules),
            "failed_rules": len(failed_rules),
            "quality_score": quality_score,
        }

        report = {
            "rule_types_evaluated": sorted({result.rule_type.value for result in evaluations}),
            "critical_failures": [
                result.to_dict()
                for result in failed_rules
                if result.severity.value == "critical"
            ],
            "warning_failures": [
                result.to_dict()
                for result in failed_rules
                if result.severity.value == "warning"
            ],
            "dataset_rows": dataframe.height,
            "dataset_columns": dataframe.width,
        }

        logger.info(
            "Quality validation completed | passed={} | failed={} | score={}",
            summary["passed_rules"],
            summary["failed_rules"],
            quality_score,
        )

        return {
            "validation_summary": summary,
            "passed_rules": [result.to_dict() for result in passed_rules],
            "failed_rules": [result.to_dict() for result in failed_rules],
            "validation_report": report,
        }
