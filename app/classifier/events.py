from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any


class FeedbackIdConflict(ValueError):
    """A feedback ID was already used for a different correction."""


class JsonlEventLogger:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._lock = Lock()
        (
            self._feedback_fingerprints,
            self._classification_request_ids,
        ) = self._load_event_indexes()

    def write(self, event: dict[str, Any]) -> None:
        with self._lock:
            self._append(event)
            if event.get("eventType") == "CLASSIFICATION":
                request_id = event.get("requestId")
                if isinstance(request_id, str) and request_id:
                    self._classification_request_ids.add(request_id)

    def has_classification(self, request_id: str) -> bool:
        """Return whether feedback can be joined to an audited prediction."""
        with self._lock:
            return request_id in self._classification_request_ids

    def write_feedback_once(self, event: dict[str, Any]) -> bool:
        """Append one feedback event, safely ignoring an identical retry.

        The caller-generated feedback ID is an idempotency key. Reusing it for
        different request/category/source data is rejected rather than letting
        one client overwrite or poison a prior correction.
        """
        feedback_id = str(event["feedbackId"])
        fingerprint = _feedback_fingerprint(event)
        with self._lock:
            existing = self._feedback_fingerprints.get(feedback_id)
            if existing is not None:
                if existing == fingerprint:
                    return False
                raise FeedbackIdConflict(feedback_id)
            self._append(event)
            self._feedback_fingerprints[feedback_id] = fingerprint
            return True

    def _append(self, event: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    def _load_event_indexes(self) -> tuple[dict[str, tuple[str, int, str]], set[str]]:
        if not self._path.exists():
            return {}, set()
        fingerprints: dict[str, tuple[str, int, str]] = {}
        classification_request_ids: set[str] = set()
        for line in self._path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            if event.get("eventType") == "CLASSIFICATION":
                request_id = event.get("requestId")
                if isinstance(request_id, str) and request_id:
                    classification_request_ids.add(request_id)
                continue
            if event.get("eventType") != "CLASSIFICATION_FEEDBACK":
                continue
            feedback_id = event.get("feedbackId")
            if not isinstance(feedback_id, str) or not feedback_id:
                continue
            try:
                fingerprints.setdefault(feedback_id, _feedback_fingerprint(event))
            except (TypeError, ValueError):
                continue
        return fingerprints, classification_request_ids


def _feedback_fingerprint(event: dict[str, Any]) -> tuple[str, int, str]:
    request_id = event["requestId"]
    good_type_id = event.get("selectedGoodTypeId", event.get("selectedRootGoodTypeId"))
    source = event["source"]
    if not isinstance(request_id, str) or not isinstance(source, str):
        raise TypeError("Feedback requestId and source must be strings")
    if isinstance(good_type_id, bool):
        raise TypeError("Feedback selectedGoodTypeId must be an integer")
    return request_id, int(good_type_id), source
