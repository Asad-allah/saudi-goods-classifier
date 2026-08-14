"""Train an offline candidate model from an exported verified-feedback dataset."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib

from app.training.supervised import TrainingDataInsufficient, train_candidate


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
        if not isinstance(row, dict):
            raise TypeError(f"JSONL row at {path}:{line_number} must be an object")
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a candidate-only root-category model from verified feedback."
    )
    parser.add_argument("--dataset", required=True, type=Path, help="Verified-feedback JSONL")
    parser.add_argument("--model-output", required=True, type=Path, help="Candidate joblib artifact")
    parser.add_argument("--metadata-output", required=True, type=Path, help="Candidate metrics JSON")
    parser.add_argument(
        "--test-fraction",
        type=float,
        default=0.2,
        help="Newest per-root fraction reserved for offline evaluation (default: 0.2)",
    )
    args = parser.parse_args()

    dataset_path = args.dataset.resolve()
    try:
        result = train_candidate(_read_jsonl(dataset_path), test_fraction=args.test_fraction)
    except (TrainingDataInsufficient, ValueError) as exc:
        parser.error(f"Candidate not trained: {exc}")

    metadata = {
        **result.metadata,
        "datasetPath": str(dataset_path),
        "trainedAt": datetime.now(UTC).isoformat(),
    }
    args.model_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": result.model, "metadata": metadata}, args.model_output)
    args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_output.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
