"""Export verified feedback from the append-only event log for offline training."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from app.training.feedback_dataset import build_verified_feedback_dataset


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
        if not isinstance(event, dict):
            raise TypeError(f"JSONL event at {path}:{line_number} must be an object")
        events.append(event)
    return events


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export validated root-category feedback as a training-candidate dataset."
    )
    parser.add_argument("--events", required=True, type=Path, help="Input classification event JSONL")
    parser.add_argument("--output", required=True, type=Path, help="Output candidate dataset JSONL")
    parser.add_argument("--report", required=True, type=Path, help="Output validation report JSON")
    args = parser.parse_args()

    events_path = args.events.resolve()
    rows, report = build_verified_feedback_dataset(_read_jsonl(events_path))
    _write_jsonl(args.output, rows)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(
            {
                **report,
                "sourceEventLog": str(events_path),
                "sourceEventLogSha256": _sha256(events_path),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
