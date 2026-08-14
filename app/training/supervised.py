"""Train an offline-only candidate classifier from verified feedback.

This module never participates in request-time classification.  It produces a
candidate artifact and evaluation metadata that must pass the promotion gates
before a later, explicit serving integration can use it.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import FeatureUnion, Pipeline

MIN_EXAMPLES_PER_GOOD_TYPE = 10
_RANDOM_SEED = 42


class TrainingDataInsufficient(ValueError):
    """Verified feedback is not yet sufficient for a trustworthy candidate."""


@dataclass(frozen=True)
class CandidateTrainingResult:
    model: Any
    metadata: dict[str, Any]


@dataclass(frozen=True)
class _Example:
    text: str
    good_type_id: int
    feedback_at: datetime


def train_candidate(
    rows: list[dict[str, Any]],
    *,
    test_fraction: float = 0.2,
) -> CandidateTrainingResult:
    """Fit and evaluate a calibrated candidate using a temporal holdout.

    Identical normalized descriptions are deduplicated.  If they have
    conflicting verified good types, every occurrence is excluded instead of
    allowing contradictory labels into either training or testing.
    """
    if not 0 < test_fraction < 0.5:
        raise ValueError("test_fraction must be greater than 0 and less than 0.5")

    examples, preparation = _prepare_examples(rows)
    counts = Counter(example.good_type_id for example in examples)
    if len(counts) < 2:
        raise TrainingDataInsufficient("at least two good types are required")
    for good_type_id, count in sorted(counts.items()):
        if count < MIN_EXAMPLES_PER_GOOD_TYPE:
            raise TrainingDataInsufficient(
                f"good_type {good_type_id} has {count} verified examples; at least "
                f"{MIN_EXAMPLES_PER_GOOD_TYPE} are required"
            )

    train_examples, test_examples = _temporal_stratified_split(examples, test_fraction)
    calibration_cv = min(
        5,
        min(Counter(item.good_type_id for item in train_examples).values()),
    )
    if calibration_cv < 2:
        raise TrainingDataInsufficient("not enough per-root training data for calibration")

    model = _build_model(calibration_cv)
    train_text = [example.text for example in train_examples]
    train_labels = [example.good_type_id for example in train_examples]
    test_text = [example.text for example in test_examples]
    test_labels = np.asarray([example.good_type_id for example in test_examples])
    model.fit(train_text, train_labels)

    probabilities = model.predict_proba(test_text)
    predicted = model.classes_[np.argmax(probabilities, axis=1)]
    top_k = min(3, len(model.classes_))
    top_indices = np.argsort(probabilities, axis=1)[:, -top_k:]
    top_labels = model.classes_[top_indices]
    top3_recall = float(
        np.mean([target in candidates for target, candidates in zip(test_labels, top_labels, strict=True)])
    )
    confidence = np.max(probabilities, axis=1)
    high_confidence = confidence >= 0.9
    high_confidence_precision = (
        float(accuracy_score(test_labels[high_confidence], predicted[high_confidence]))
        if np.any(high_confidence)
        else None
    )

    metadata = {
        "artifactFormat": "dandan-feedback-tfidf-v1",
        "candidateModelVersion": _candidate_version(examples),
        "datasetSha256": _dataset_sha256(examples),
        "split": {
            "strategy": "temporal-per-root",
            "testFraction": test_fraction,
            "trainRows": len(train_examples),
            "testRows": len(test_examples),
            "testStartsAfter": min(example.feedback_at for example in test_examples).isoformat(),
        },
        "preparation": preparation,
        "provenance": _provenance(rows),
        "classCounts": {str(root_id): count for root_id, count in sorted(counts.items())},
        "features": {
            "wordNgrams": [1, 2],
            "characterNgrams": [2, 5],
            "characterWeight": 0.7,
        },
        "calibration": {"method": "sigmoid", "cv": calibration_cv},
        "metrics": {
            "top1Accuracy": round(float(accuracy_score(test_labels, predicted)), 6),
            "top3Recall": round(top3_recall, 6),
            "highConfidenceThreshold": 0.9,
            "highConfidenceCoverage": round(float(np.mean(high_confidence)), 6),
            "highConfidenceSampleCount": int(np.count_nonzero(high_confidence)),
            "highConfidencePrecision": (
                round(high_confidence_precision, 6)
                if high_confidence_precision is not None
                else None
            ),
        },
        "promotionStatus": "CANDIDATE_ONLY",
    }
    return CandidateTrainingResult(model=model, metadata=metadata)


def _prepare_examples(rows: list[dict[str, Any]]) -> tuple[list[_Example], dict[str, int]]:
    grouped: dict[str, list[_Example]] = defaultdict(list)
    rejected_rows = 0
    for row in rows:
        text = _nonempty_string(row.get("normalizedText"))
        good_type_id = _positive_int(row.get("goodTypeId", row.get("rootGoodTypeId")))
        feedback_at = _timestamp(row.get("feedbackRecordedAt"))
        if text is None or good_type_id is None or feedback_at is None:
            rejected_rows += 1
            continue
        grouped[text].append(
            _Example(
                text=text,
                good_type_id=good_type_id,
                feedback_at=feedback_at,
            )
        )

    examples: list[_Example] = []
    conflicting_texts = 0
    duplicate_rows = 0
    for occurrences in grouped.values():
        labels = {item.good_type_id for item in occurrences}
        if len(labels) != 1:
            conflicting_texts += 1
            continue
        duplicate_rows += max(0, len(occurrences) - 1)
        examples.append(max(occurrences, key=lambda item: item.feedback_at))

    return sorted(examples, key=lambda item: (item.feedback_at, item.text)), {
        "inputRows": len(rows),
        "rejectedRows": rejected_rows,
        "duplicateRows": duplicate_rows,
        "conflictingNormalizedTexts": conflicting_texts,
        "usableRows": len(examples),
    }


def _provenance(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Retain the catalog and serving-model lineage used to collect labels."""
    catalog_versions = sorted(
        {value for row in rows if (value := _nonempty_string(row.get("catalogVersion")))}
    )
    source_model_versions = sorted(
        {value for row in rows if (value := _nonempty_string(row.get("modelVersion")))}
    )
    return {
        "catalogVersions": catalog_versions,
        "sourceModelVersions": source_model_versions,
    }


def _temporal_stratified_split(
    examples: list[_Example], test_fraction: float
) -> tuple[list[_Example], list[_Example]]:
    per_good_type: dict[int, list[_Example]] = defaultdict(list)
    for example in examples:
        per_good_type[example.good_type_id].append(example)

    train: list[_Example] = []
    test: list[_Example] = []
    for good_type_examples in per_good_type.values():
        ordered = sorted(good_type_examples, key=lambda item: (item.feedback_at, item.text))
        test_size = max(1, math.ceil(len(ordered) * test_fraction))
        train.extend(ordered[:-test_size])
        test.extend(ordered[-test_size:])
    return train, test


def _build_model(calibration_cv: int) -> Pipeline:
    features = FeatureUnion(
        [
            (
                "word",
                TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True),
            ),
            (
                "character",
                TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True),
            ),
        ],
        transformer_weights={"word": 1.0, "character": 0.7},
    )
    base_estimator = LogisticRegression(
        class_weight="balanced",
        max_iter=1_000,
        random_state=_RANDOM_SEED,
    )
    return Pipeline(
        [
            ("features", features),
            (
                "classifier",
                CalibratedClassifierCV(
                    estimator=base_estimator,
                    method="sigmoid",
                    cv=calibration_cv,
                    ensemble=False,
                    n_jobs=1,
                ),
            ),
        ]
    )


def _dataset_sha256(examples: list[_Example]) -> str:
    payload = [
        {
            "text": item.text,
            "goodTypeId": item.good_type_id,
            "feedbackRecordedAt": item.feedback_at.isoformat(),
        }
        for item in examples
    ]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _candidate_version(examples: list[_Example]) -> str:
    return f"feedback-tfidf-{_dataset_sha256(examples)[:12]}"


def _nonempty_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        result = datetime.fromisoformat(value)
    except ValueError:
        return None
    return result if result.tzinfo is not None else None
