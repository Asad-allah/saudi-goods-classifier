import pytest

from app.training.supervised import TrainingDataInsufficient, train_candidate


def test_training_refuses_to_fit_when_a_root_has_too_few_verified_examples() -> None:
    rows = [
        {
            "normalizedText": "كياس نفايات",
            "goodTypeId": 141,
            "feedbackRecordedAt": "2026-08-13T00:00:00+00:00",
        },
        *[
            {
                "normalizedText": f"عبوة بلاستيكية {index}",
                "goodTypeId": 5,
                "feedbackRecordedAt": f"2026-08-{index:02d}T00:00:00+00:00",
            }
            for index in range(1, 11)
        ],
    ]

    with pytest.raises(TrainingDataInsufficient, match="at least 10"):
        train_candidate(rows)


def test_training_builds_a_calibrated_candidate_from_temporally_held_out_rows() -> None:
    examples = {
        12: "شوكولاتة وحلوى",
        141: "كياس نفايات سوداء",
        5: "عبوات بلاستيك صناعية",
    }
    rows = [
        {
            "normalizedText": f"{text} نموذج {index}",
            "goodTypeId": root_id,
            "feedbackRecordedAt": f"2026-08-{index:02d}T00:00:00+00:00",
            "catalogVersion": "catalog-2026-08",
            "modelVersion": "retrieval-model-1",
        }
        for root_id, text in examples.items()
        for index in range(1, 11)
    ]

    result = train_candidate(rows)

    assert result.metadata["promotionStatus"] == "CANDIDATE_ONLY"
    assert result.metadata["split"] == {
        "strategy": "temporal-per-root",
        "testFraction": 0.2,
        "trainRows": 24,
        "testRows": 6,
        "testStartsAfter": "2026-08-09T00:00:00+00:00",
    }
    assert result.metadata["calibration"] == {"method": "sigmoid", "cv": 5}
    assert result.metadata["provenance"] == {
        "catalogVersions": ["catalog-2026-08"],
        "sourceModelVersions": ["retrieval-model-1"],
    }
    assert result.metadata["metrics"]["top1Accuracy"] >= 0.8
    assert result.metadata["metrics"]["highConfidenceSampleCount"] == round(
        result.metadata["metrics"]["highConfidenceCoverage"]
        * result.metadata["split"]["testRows"]
    )
    assert result.model.predict(["كياس نفايات سوداء"])[0] == 141
