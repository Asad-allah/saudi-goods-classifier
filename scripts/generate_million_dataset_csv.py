#!/usr/bin/env python3
"""Streaming generator for 1 Million unique bilingual goods dataset exported to CSV and Excel."""

from __future__ import annotations
import argparse
import csv
import json
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from app.data_engine.ontology import ROOT_ONTOLOGY
from app.data_engine.generator import LogisticsDatasetGenerator
from app.data_engine.sanitizer import DatasetSanitizer
from app.data_engine.validator import ZeroConflictValidator


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate 1,000,000 unique bilingual logistics records in CSV and JSONL."
    )
    parser.add_argument(
        "--target-total",
        type=int,
        default=1000000,
        help="Total dataset target size (default: 1,000,000).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="storage/training/million_dataset",
        help="Output directory for generated CSV files.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )

    args = parser.parse_args()

    num_roots = len(ROOT_ONTOLOGY)
    target_per_root = int(args.target_total / num_roots) + 1
    total_target = target_per_root * num_roots

    print("=" * 70)
    print(f"🚀 MASSIVE 1-MILLION BILINGUAL DATASET GENERATION PIPELINE")
    print("=" * 70)
    print(f"🎯 Target Total:        {total_target:,} records ({target_per_root:,} per root x {num_roots} roots)")
    print(f"🌐 Languages:           Arabic (~60%), English (~25%), Mixed (~15%)")
    print(f"📁 Output Directory:    {args.output_dir}/")
    print(f"💾 File Formats:        CSV (UTF-8-SIG for Microsoft Excel & Pandas)")
    print("=" * 70 + "\n")

    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    generator = LogisticsDatasetGenerator(seed=args.seed)
    sanitizer = DatasetSanitizer()
    validator = ZeroConflictValidator()

    start_time = time.perf_counter()
    all_clean_records: list[dict[str, int | str]] = []

    print("⏳ [1/4] Generating bilingual samples across all 37 root categories...")
    for idx, (root_id, spec) in enumerate(ROOT_ONTOLOGY.items(), start=1):
        cat_start = time.perf_counter()
        # Generate with a buffer to ensure target after sanitization
        buffer_target = int(target_per_root * 1.05)
        raw_samples = generator.generate_category_samples(root_id, target_count=buffer_target)

        cat_records: list[dict[str, int | str]] = []
        for text in raw_samples:
            if sanitizer.is_acceptable(text):
                cleaned = sanitizer.clean(text)
                cat_records.append({
                    "text": cleaned,
                    "root_id": root_id,
                    "root_name_ar": spec.name_ar,
                    "root_name_en": spec.name_en,
                    "language": "AR" if any("\u0600" <= c <= "\u06ff" for c in cleaned) and not any(c.isascii() and c.isalpha() for c in cleaned) else ("EN" if all(not ("\u0600" <= c <= "\u06ff") for c in cleaned) else "MIXED"),
                    "source": "saudi_logistics_gold_generator",
                })

        # Trim to exact target
        cat_records = cat_records[:target_per_root]
        all_clean_records.extend(cat_records)
        cat_elapsed = time.perf_counter() - cat_start
        print(f"  [{idx:02d}/37] Root {root_id:3d} ({spec.name_ar:25s} | {spec.name_en:25s}) -> {len(cat_records):,d} rows ({cat_elapsed:.2f}s)")

    print(f"\n⏳ [2/4] Validating and checking cross-category zero-conflict across {len(all_clean_records):,} rows...")
    val_start = time.perf_counter()
    final_dataset, report = validator.validate_and_filter(all_clean_records)
    print(f"  Validation finished in {time.perf_counter() - val_start:.2f}s. Conflict Rate: {report.conflict_rate_pct:.4f}%")

    print("\n⏳ [3/4] Performing Stratified Split (80% Train, 10% Val, 10% Test Gold)...")
    split_by_cat: dict[int, list[dict[str, int | str]]] = {}
    for row in final_dataset:
        split_by_cat.setdefault(int(row["root_id"]), []).append(row)

    train_rows: list[dict[str, int | str]] = []
    val_rows: list[dict[str, int | str]] = []
    test_rows: list[dict[str, int | str]] = []

    rng = random.Random(args.seed)
    for rid, items in split_by_cat.items():
        rng.shuffle(items)
        n = len(items)
        n_train = int(n * 0.80)
        n_val = int(n * 0.10)

        train_rows.extend(items[:n_train])
        val_rows.extend(items[n_train:n_train + n_val])
        test_rows.extend(items[n_train + n_val:])

    # Shuffle splits
    rng.shuffle(train_rows)
    rng.shuffle(val_rows)
    rng.shuffle(test_rows)
    rng.shuffle(final_dataset)

    print("\n⏳ [4/4] Exporting to CSV (UTF-8 with BOM for Excel compatibility)...")
    csv_fields = ["text", "root_id", "root_name_ar", "root_name_en", "language", "source"]

    def write_csv(filepath: Path, records: list[dict[str, Any]]) -> None:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(records)

    write_csv(out_path / "dataset_1m_complete.csv", final_dataset)
    write_csv(out_path / "train_800k.csv", train_rows)
    write_csv(out_path / "val_100k.csv", val_rows)
    write_csv(out_path / "test_gold_100k.csv", test_rows)

    audit_summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_records": len(final_dataset),
        "train_records": len(train_rows),
        "val_records": len(val_rows),
        "test_records": len(test_rows),
        "categories_count": len(report.category_counts),
        "unique_vocab_size": report.lexical_vocab_size,
        "conflict_rate_pct": report.conflict_rate_pct,
        "is_zero_conflict": report.is_zero_conflict,
        "files_exported": [
            "dataset_1m_complete.csv",
            "train_800k.csv",
            "val_100k.csv",
            "test_gold_100k.csv",
        ],
        "category_distribution": report.category_counts,
    }

    with open(out_path / "audit_report_1m.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, ensure_ascii=False, indent=2)

    total_elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 70)
    print("🎉 1-MILLION BILINGUAL DATASET SUCCESSFULLY GENERATED & EXPORTED")
    print("=" * 70)
    print(f"📊 Total Records:       {len(final_dataset):,}")
    print(f"🚆 Train Set (80%):     {len(train_rows):,} rows -> train_800k.csv")
    print(f"🔍 Val Set (10%):       {len(val_rows):,} rows -> val_100k.csv")
    print(f"🏆 Test Gold Set (10%): {len(test_rows):,} rows -> test_gold_100k.csv")
    print(f"🏛️ Categories Covered:  {len(report.category_counts)} / 37 roots")
    print(f"📚 Unique Words Vocab:  {report.lexical_vocab_size:,}")
    print(f"🛡️ Conflict Rate:       {report.conflict_rate_pct:.4f}% (Zero Conflict: {report.is_zero_conflict})")
    print(f"⏱️ Total Generation Time: {total_elapsed:.2f}s")
    print(f"💾 Excel/CSV Location:  {args.output_dir}/")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
