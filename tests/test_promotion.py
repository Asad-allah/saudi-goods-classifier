from app.training.promotion import PromotionThresholds, evaluate_candidate_promotion


def test_promotion_approves_a_candidate_that_beats_the_same_dataset_baseline() -> None:
    candidate = {
        "promotionStatus": "CANDIDATE_ONLY",
        "datasetSha256": "same-evaluation-data",
        "split": {"testRows": 160},
        "metrics": {
            "top1Accuracy": 0.92,
            "top3Recall": 0.98,
            "highConfidencePrecision": 0.96,
            "highConfidenceSampleCount": 64,
        },
    }
    baseline = {
        "evaluationDatasetSha256": "same-evaluation-data",
        "metrics": {
            "top1Accuracy": 0.91,
            "top3Recall": 0.97,
            "highConfidencePrecision": 0.95,
        },
    }

    report = evaluate_candidate_promotion(candidate, baseline)

    assert report["approved"] is True
    assert report["failedGates"] == []
    assert report["thresholds"] == {
        "minTop1Accuracy": 0.9,
        "minTop3Recall": 0.97,
        "minHighConfidencePrecision": 0.95,
        "minTestRows": 100,
        "minHighConfidenceSamples": 30,
    }


def test_promotion_rejects_mismatched_baseline_and_insufficient_evidence() -> None:
    candidate = {
        "promotionStatus": "CANDIDATE_ONLY",
        "datasetSha256": "candidate-data",
        "split": {"testRows": 12},
        "metrics": {
            "top1Accuracy": 0.99,
            "top3Recall": 0.99,
            "highConfidencePrecision": 1.0,
            "highConfidenceSampleCount": 2,
        },
    }
    baseline = {
        "evaluationDatasetSha256": "different-data",
        "metrics": {
            "top1Accuracy": 0.5,
            "top3Recall": 0.5,
            "highConfidencePrecision": 0.5,
        },
    }

    report = evaluate_candidate_promotion(candidate, baseline)

    assert report["approved"] is False
    assert {failure["code"] for failure in report["failedGates"]} == {
        "EVALUATION_DATASET_MISMATCH",
        "INSUFFICIENT_TEST_ROWS",
        "INSUFFICIENT_HIGH_CONFIDENCE_SAMPLES",
    }


def test_promotion_rejects_metric_regression_and_can_use_stricter_thresholds() -> None:
    candidate = {
        "promotionStatus": "CANDIDATE_ONLY",
        "datasetSha256": "same-data",
        "split": {"testRows": 150},
        "metrics": {
            "top1Accuracy": 0.9,
            "top3Recall": 0.97,
            "highConfidencePrecision": 0.95,
            "highConfidenceSampleCount": 50,
        },
    }
    baseline = {
        "evaluationDatasetSha256": "same-data",
        "metrics": {
            "top1Accuracy": 0.94,
            "top3Recall": 0.98,
            "highConfidencePrecision": 0.97,
        },
    }

    report = evaluate_candidate_promotion(
        candidate,
        baseline,
        thresholds=PromotionThresholds(min_top1_accuracy=0.91),
    )

    assert report["approved"] is False
    assert {failure["code"] for failure in report["failedGates"]} == {
        "TOP1_BELOW_THRESHOLD",
        "TOP1_REGRESSION",
        "TOP3_REGRESSION",
        "HIGH_CONFIDENCE_PRECISION_REGRESSION",
    }


def test_promotion_rejects_non_finite_metrics() -> None:
    candidate = {
        "promotionStatus": "CANDIDATE_ONLY",
        "datasetSha256": "same-data",
        "split": {"testRows": 120},
        "metrics": {
            "top1Accuracy": float("nan"),
            "top3Recall": 0.98,
            "highConfidencePrecision": 0.96,
            "highConfidenceSampleCount": 40,
        },
    }
    baseline = {
        "evaluationDatasetSha256": "same-data",
        "metrics": {
            "top1Accuracy": 0.9,
            "top3Recall": 0.97,
            "highConfidencePrecision": 0.95,
        },
    }

    report = evaluate_candidate_promotion(candidate, baseline)

    assert report["approved"] is False
    assert any(item["code"] == "TOP1_BELOW_THRESHOLD_MISSING" for item in report["failedGates"])
