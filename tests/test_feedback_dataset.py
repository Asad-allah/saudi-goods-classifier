from app.training.feedback_dataset import build_verified_feedback_dataset


def test_dataset_builder_keeps_only_verified_non_conflicting_labels() -> None:
    events = [
        {
            "eventType": "CLASSIFICATION",
            "requestId": "confirmed-correction",
            "text": "كياس زباله",
            "normalizedText": "كياس زباله",
            "catalogVersion": "catalog-a",
            "modelVersion": "model-a",
        },
        {
            "eventType": "CLASSIFICATION_FEEDBACK",
            "feedbackId": "feedback-1",
            "requestId": "confirmed-correction",
            "selectedRootGoodTypeId": 141,
            "source": "OPERATOR_REVIEW",
            "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
        },
        {
            "eventType": "CLASSIFICATION",
            "requestId": "driver-only",
            "text": "حليب أطفال",
            "normalizedText": "حليب اطفال",
            "catalogVersion": "catalog-a",
            "modelVersion": "model-a",
        },
        {
            "eventType": "CLASSIFICATION_FEEDBACK",
            "feedbackId": "feedback-2",
            "requestId": "driver-only",
            "selectedRootGoodTypeId": 12,
            "source": "DRIVER_SELECTION",
            "trainingEligibility": "PENDING_REVIEW",
        },
        {
            "eventType": "CLASSIFICATION",
            "requestId": "conflict",
            "text": "كياس استخدام عام",
            "normalizedText": "كياس استخدام عام",
            "catalogVersion": "catalog-a",
            "modelVersion": "model-a",
        },
        {
            "eventType": "CLASSIFICATION_FEEDBACK",
            "feedbackId": "feedback-3",
            "requestId": "conflict",
            "selectedRootGoodTypeId": 141,
            "source": "OPERATOR_REVIEW",
            "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
        },
        {
            "eventType": "CLASSIFICATION_FEEDBACK",
            "feedbackId": "feedback-4",
            "requestId": "conflict",
            "selectedRootGoodTypeId": 163,
            "source": "OPERATOR_REVIEW",
            "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
        },
    ]

    rows, report = build_verified_feedback_dataset(events)

    assert rows == [
        {
            "feedbackId": "feedback-1",
            "requestId": "confirmed-correction",
            "text": "كياس زباله",
            "normalizedText": "كياس زباله",
            "goodTypeId": 141,
            "rootGoodTypeId": 141,
            "catalogVersion": "catalog-a",
            "modelVersion": "model-a",
            "classificationRecordedAt": "",
            "feedbackRecordedAt": "",
        }
    ]
    assert report == {
        "classificationEvents": 3,
        "verifiedFeedbackEvents": 3,
        "exportedRows": 1,
        "skippedUnverifiedFeedback": 1,
        "quarantinedConflictingRequests": 1,
        "quarantinedOrphanFeedback": 0,
        "duplicateFeedbackIds": 0,
    }


def test_dataset_builder_deduplicates_feedback_ids_and_quarantines_orphans() -> None:
    events = [
        {
            "eventType": "CLASSIFICATION_FEEDBACK",
            "feedbackId": "duplicate-feedback",
            "requestId": "missing-request",
            "selectedRootGoodTypeId": 141,
            "source": "OPERATOR_REVIEW",
            "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
        },
        {
            "eventType": "CLASSIFICATION_FEEDBACK",
            "feedbackId": "duplicate-feedback",
            "requestId": "missing-request",
            "selectedRootGoodTypeId": 141,
            "source": "OPERATOR_REVIEW",
            "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
        },
    ]

    rows, report = build_verified_feedback_dataset(events)

    assert rows == []
    assert report["duplicateFeedbackIds"] == 1
    assert report["quarantinedOrphanFeedback"] == 1


def test_dataset_builder_preserves_event_timestamps_for_temporal_evaluation() -> None:
    rows, _ = build_verified_feedback_dataset(
        [
            {
                "eventType": "CLASSIFICATION",
                "requestId": "time-aware-request",
                "recordedAt": "2026-08-12T09:00:00+00:00",
                "text": "كياس نفايات",
                "normalizedText": "كياس نفايات",
            },
            {
                "eventType": "CLASSIFICATION_FEEDBACK",
                "feedbackId": "time-aware-feedback",
                "requestId": "time-aware-request",
                "recordedAt": "2026-08-12T10:00:00+00:00",
                "selectedRootGoodTypeId": 141,
                "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
            },
        ]
    )

    assert rows[0]["classificationRecordedAt"] == "2026-08-12T09:00:00+00:00"
    assert rows[0]["feedbackRecordedAt"] == "2026-08-12T10:00:00+00:00"
