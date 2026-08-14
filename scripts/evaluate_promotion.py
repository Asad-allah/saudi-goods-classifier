"""Run offline promotion gates against a candidate and frozen baseline report."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.training.promotion import evaluate_candidate_promotion


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON object from {path}") from exc
    if not isinstance(value, dict):
        raise TypeError(f"JSON document at {path} must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate an offline candidate against a frozen baseline; never deploys it."
    )
    parser.add_argument("--candidate", required=True, type=Path, help="Candidate metrics JSON")
    parser.add_argument("--baseline", required=True, type=Path, help="Baseline metrics JSON")
    parser.add_argument("--report", required=True, type=Path, help="Promotion decision JSON")
    args = parser.parse_args()

    try:
        decision = evaluate_candidate_promotion(
            _read_object(args.candidate.resolve()),
            _read_object(args.baseline.resolve()),
        )
    except (OSError, TypeError, ValueError) as exc:
        parser.error(str(exc))

    report = {
        **decision,
        "evaluatedAt": datetime.now(UTC).isoformat(),
        "candidatePath": str(args.candidate.resolve()),
        "baselinePath": str(args.baseline.resolve()),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["approved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
