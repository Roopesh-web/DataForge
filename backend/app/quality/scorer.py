from app.quality.models import RuleEvaluationResult


def calculate_quality_score(evaluations: list[RuleEvaluationResult]) -> float:
    if not evaluations:
        return 100.0

    weighted_total = 0.0
    weighted_passed = 0.0

    severity_weights = {
        "critical": 3.0,
        "warning": 2.0,
        "info": 1.0,
    }

    for result in evaluations:
        weight = severity_weights.get(result.severity.value, 1.0)
        weighted_total += weight
        if result.passed:
            weighted_passed += weight

    score = round((weighted_passed / weighted_total) * 100, 2)
    return max(0.0, min(score, 100.0))
