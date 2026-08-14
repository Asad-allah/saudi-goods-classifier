"""Build a conservative training-candidate set from append-only feedback logs.

This module deliberately does not train or deploy a model.  Its job is to
preserve provenance and quarantine ambiguous data before it can influence a
future classifier.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

_CLASSIFICATION_EVENT = "CLASSIFICATION"
_FEEDBACK_EVENT = "CLASSIFICATION_FEEDBACK"
_TRAINING_CANDIDATE = "CANDIDATE_AFTER_VALIDATION"


def build_verified_feedback_dataset(
    events: Iterable[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Join classification events with verified, non-conflicting corrections.

    A correction is useful only when its original text is available and all
    verified reviewers agree on a single good_type.  Driver selections and demo
    selections remain logged but cannot enter the exported dataset.
    """
    classifications: dict[str, Mapping[str, Any]] = {}
    verified_feedback: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    seen_feedback_ids: set[str] = set()
    report = {
        "classificationEvents": 0,
        "verifiedFeedbackEvents": 0,
        "exportedRows": 0,
        "skippedUnverifiedFeedback": 0,
        "quarantinedConflictingRequests": 0,
        "quarantinedOrphanFeedback": 0,
        "duplicateFeedbackIds": 0,
    }

    for event in events:
        event_type = event.get("eventType")
        if event_type == _CLASSIFICATION_EVENT:
            request_id = _nonempty_string(event.get("requestId"))
            if request_id is None:
                continue
            report["classificationEvents"] += 1
            classifications[request_id] = event
            continue

        if event_type != _FEEDBACK_EVENT:
            continue
        if event.get("trainingEligibility") != _TRAINING_CANDIDATE:
            report["skippedUnverifiedFeedback"] += 1
            continue

        report["verifiedFeedbackEvents"] += 1
        feedback_id = _nonempty_string(event.get("feedbackId"))
        request_id = _nonempty_string(event.get("requestId"))
        good_type_id = _event_good_type_id(event)
        if feedback_id is None or request_id is None or good_type_id is None:
            report["quarantinedOrphanFeedback"] += 1
            continue
        if feedback_id in seen_feedback_ids:
            report["duplicateFeedbackIds"] += 1
            continue
        seen_feedback_ids.add(feedback_id)
        verified_feedback[request_id].append(event)

    rows: list[dict[str, Any]] = []
    for request_id in sorted(verified_feedback):
        feedback_events = verified_feedback[request_id]
        classification = classifications.get(request_id)
        if classification is None:
            report["quarantinedOrphanFeedback"] += len(feedback_events)
            continue

        good_type_ids = {
            _event_good_type_id(event)
            for event in feedback_events
        }
        good_type_ids.discard(None)
        if len(good_type_ids) != 1:
            report["quarantinedConflictingRequests"] += 1
            continue

        text = _nonempty_string(classification.get("text"))
        normalized_text = _nonempty_string(classification.get("normalizedText"))
        if text is None or normalized_text is None:
            report["quarantinedOrphanFeedback"] += len(feedback_events)
            continue

        feedback = feedback_events[0]
        rows.append(
            {
                "feedbackId": feedback["feedbackId"],
                "requestId": request_id,
                "text": text,
                "normalizedText": normalized_text,
                "goodTypeId": next(iter(good_type_ids)),
                "rootGoodTypeId": _positive_int(
                    feedback.get("selectedRootGoodTypeId")
                ),
                "catalogVersion": classification.get("catalogVersion", ""),
                "modelVersion": classification.get("modelVersion", ""),
                "classificationRecordedAt": classification.get("recordedAt", ""),
                "feedbackRecordedAt": feedback.get("recordedAt", ""),
            }
        )

    report["exportedRows"] = len(rows)
    return rows, report


def _nonempty_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def _event_good_type_id(event: Mapping[str, Any]) -> int | None:
    return _positive_int(
        event.get("selectedGoodTypeId", event.get("selectedRootGoodTypeId"))
    )
