from __future__ import annotations

import argparse
import csv
from pathlib import Path

from app.catalog.importer import load_catalog_from_sql
from app.classifier.service import RootCategoryClassifier


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate classifier against a CSV gold set.")
    parser.add_argument("--source", required=True, help="Path to sub_db.sql")
    parser.add_argument(
        "--gold",
        required=True,
        help="CSV with columns text,good_type_id; root_good_type_id is accepted for old files.",
    )
    args = parser.parse_args()

    classifier = RootCategoryClassifier(load_catalog_from_sql(args.source))
    with Path(args.gold).open(encoding="utf-8-sig", newline="") as gold_file:
        rows = list(csv.DictReader(gold_file))
    if not rows:
        raise SystemExit("Gold set is empty")

    top1 = 0
    top3 = 0
    no_review_correct = 0
    no_review_total = 0
    for index, row in enumerate(rows, start=1):
        expected = int(row.get("good_type_id") or row["root_good_type_id"])
        result = classifier.classify(request_id=str(index), text=row["text"])
        alternatives = [candidate.good_type_id for candidate in result.alternatives]
        top1 += int(
            result.top_category is not None
            and result.top_category.good_type_id == expected
        )
        top3 += int(expected in alternatives)
        if not result.requires_review:
            no_review_total += 1
            no_review_correct += int(
                result.top_category is not None
                and result.top_category.good_type_id == expected
            )

    total = len(rows)
    precision = (no_review_correct / no_review_total) if no_review_total else 0.0
    print(f"Top-1 Accuracy: {top1 / total:.3f}")
    print(f"Top-3 Recall:   {top3 / total:.3f}")
    print(f"No-review precision: {precision:.3f} ({no_review_total} cases)")


if __name__ == "__main__":
    main()
