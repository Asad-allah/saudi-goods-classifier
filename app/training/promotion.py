"""Evaluate whether an offline candidate may enter a controlled canary.

An approved report is necessary but not sufficient for production deployment:
release control still owns the canary and rollback decision.  This module never
loads model artifacts and never changes the request-time classifier.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromotionThresholds:
    min_top1_accuracy: float = 0.90
    min_top3_recall: float = 0.97
    min_high_confidence_precision: float = 0.95
    min_test_rows: int = 100
    min_high_confidence_samples: int = 30


def evaluate_candidate_promotion(
    candidate: Mapping[str, Any],
    baseline: Mapping[str, Any],
    *,
    thresholds: PromotionThresholds | None = None,
) -> dict[str, Any]:
    """Return an auditable decision without promoting or loading a model.

    The baseline is deliberately a separate input because the comparison is
    meaningful only when both systems ran on the same frozen evaluation set.
    Invalid or incomplete evidence fails closed.
    """
    active_thresholds = thresholds or PromotionThresholds()
    failures: list[dict[str, str]] = []
    candidate_metrics = _mapping(candidate.get("metrics"))
    baseline_metrics = _mapping(baseline.get("metrics"))

    if candidate.get("promotionStatus") != "CANDIDATE_ONLY":
        _fail(
            failures,
            "CANDIDATE_STATUS_INVALID",
            "Candidate metadata must have promotionStatus CANDIDATE_ONLY.",
        )

    dataset_sha = _string(candidate.get("datasetSha256"))
    baseline_dataset_sha = _string(baseline.get("evaluationDatasetSha256"))
    if dataset_sha is None or baseline_dataset_sha is None or dataset_sha != baseline_dataset_sha:
        _fail(
            failures,
            "EVALUATION_DATASET_MISMATCH",
            "Candidate and baseline must use the same evaluation dataset SHA-256.",
        )

    split = _mapping(candidate.get("split"))
    test_rows = _integer(split.get("testRows"))
    high_confidence_samples = _integer(candidate_metrics.get("highConfidenceSampleCount"))
    _minimum_gate(
        failures,
        "INSUFFICIENT_TEST_ROWS",
        test_rows,
        active_thresholds.min_test_rows,
        "held-out test rows",
    )
    _minimum_gate(
        failures,
        "INSUFFICIENT_HIGH_CONFIDENCE_SAMPLES",
        high_confidence_samples,
        active_thresholds.min_high_confidence_samples,
        "high-confidence test samples",
    )

    _metric_gate(
        failures,
        candidate_metrics,
        baseline_metrics,
        metric_key="top1Accuracy",
        minimum=active_thresholds.min_top1_accuracy,
        below_code="TOP1_BELOW_THRESHOLD",
        regression_code="TOP1_REGRESSION",
    )
    _metric_gate(
        failures,
        candidate_metrics,
        baseline_metrics,
        metric_key="top3Recall",
        minimum=active_thresholds.min_top3_recall,
        below_code="TOP3_BELOW_THRESHOLD",
        regression_code="TOP3_REGRESSION",
    )
    _metric_gate(
        failures,
        candidate_metrics,
        baseline_metrics,
        metric_key="highConfidencePrecision",
        minimum=active_thresholds.min_high_confidence_precision,
        below_code="HIGH_CONFIDENCE_PRECISION_BELOW_THRESHOLD",
        regression_code="HIGH_CONFIDENCE_PRECISION_REGRESSION",
    )

    return {
        "approved": not failures,
        "candidateModelVersion": candidate.get("candidateModelVersion"),
        "evaluationDatasetSha256": dataset_sha,
        "thresholds": {
            "minTop1Accuracy": active_thresholds.min_top1_accuracy,
            "minTop3Recall": active_thresholds.min_top3_recall,
            "minHighConfidencePrecision": active_thresholds.min_high_confidence_precision,
            "minTestRows": active_thresholds.min_test_rows,
            "minHighConfidenceSamples": active_thresholds.min_high_confidence_samples,
        },
        "candidateMetrics": dict(candidate_metrics),
        "baselineMetrics": dict(baseline_metrics),
        "failedGates": failures,
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _integer(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _number(value: Any) -> float | None:
    if not isinstance(value, (float, int)) or isinstance(value, bool):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _fail(failures: list[dict[str, str]], code: str, message: str) -> None:
    failures.append({"code": code, "message": message})


def _minimum_gate(
    failures: list[dict[str, str]],
    code: str,
    observed: int | None,
    minimum: int,
    label: str,
) -> None:
    if observed is None or observed < minimum:
        _fail(failures, code, f"Require at least {minimum} {label}; observed {observed}.")


def _metric_gate(
    failures: list[dict[str, str]],
    candidate: Mapping[str, Any],
    baseline: Mapping[str, Any],
    *,
    metric_key: str,
    minimum: float,
    below_code: str,
    regression_code: str,
) -> None:
    candidate_value = _number(candidate.get(metric_key))
    baseline_value = _number(baseline.get(metric_key))
    if candidate_value is None:
        _fail(failures, f"{below_code}_MISSING", f"Candidate metric {metric_key} is missing.")
        return
    if candidate_value < minimum:
        _fail(
            failures,
            below_code,
            f"Candidate {metric_key} must be at least {minimum}; observed {candidate_value}.",
        )
    if baseline_value is None:
        _fail(failures, f"{regression_code}_MISSING", f"Baseline metric {metric_key} is missing.")
    elif candidate_value < baseline_value:
        _fail(
            failures,
            regression_code,
            f"Candidate {metric_key} {candidate_value} is below baseline {baseline_value}.",
        )
