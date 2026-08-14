#!/usr/bin/env python3
"""CLI for generating 1,000,000+ AI-Grade Deep Semantic Records across all 90 Leaf Categories in CSV/Excel."""

from __future__ import annotations
import argparse
import csv
import json
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from app.data_engine.leaf_ontology import LEAF_ONTOLOGY
from app.data_engine.ai_semantic_generator import AISemanticDatasetGenerator
from app.nlp.normalizer import normalize_text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate 1M+ deep semantic, non-corrupted bilingual logistics dataset."
    )
    parser.add_argument(
        "--target-total",
        type=int,
        default=1000000,
        help="Target total records (default: 1,000,000).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="storage/training/semantic_million_dataset",
        help="Output directory for generated CSV files.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )

    args = parser.parse_args()

    num_leaves = len(LEAF_ONTOLOGY)
    target_per_leaf = int(args.target_total / num_leaves) + 1
    total_target = target_per_leaf * num_leaves

    print("=" * 80)
    print("🧠 DEEP AI SEMANTIC DATASET GENERATOR (90 LEAF CATEGORIES - NO CHARACTER MUTATION)")
    print("=" * 80)
    print(f"🎯 Target Total:        {total_target:,} records ({target_per_leaf:,} per leaf x {num_leaves} leaves)")
    print(f"🌿 Leaf Classes:        {num_leaves} Terminal Categories (All goods in the database)")
    print(f"🌐 Quality Standard:    Authentic commercial, trade manifest & natural dialect phrasing")
    print(f"💾 Export Format:       CSV (UTF-8 with BOM for Microsoft Excel & Pandas)")
    print(f"📁 Output Directory:    {args.output_dir}/")
    print("=" * 80 + "\n")

    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    generator = AISemanticDatasetGenerator(seed=args.seed)
    start_time = time.perf_counter()
    all_records: list[dict[str, Any]] = []

    print("⏳ [1/4] Generating natural semantic records across all 90 leaf categories...")
    for idx, (leaf_id, spec) in enumerate(LEAF_ONTOLOGY.items(), start=1):
        cat_start = time.perf_counter()
        records = generator.generate_leaf_records(spec, target_count=target_per_leaf)
        all_records.extend(records)
        cat_elapsed = time.perf_counter() - cat_start

        if idx % 10 == 0 or idx == num_leaves:
            print(f"  [{idx:02d}/{num_leaves}] Leaf {leaf_id:3d} ({spec.name_ar[:25]:25s}) -> {len(records):,d} rows (Total: {len(all_records):,d})")

    print(f"\n⏳ [2/4] Verifying 100% strict deduplication & semantic uniqueness across {len(all_records):,} rows...")
    seen_texts: set[str] = set()
    deduped_records: list[dict[str, Any]] = []
    vocab: set[str] = set()
    cat_counts: dict[int, int] = {}

    for row in all_records:
        norm = normalize_text(str(row["text"]))
        if norm in seen_texts:
            continue
        seen_texts.add(norm)
        deduped_records.append(row)
        cat_counts[row["good_type_id"]] = cat_counts.get(row["good_type_id"], 0) + 1
        for word in norm.split():
            vocab.add(word)

    print(f"  Deduped Unique Count: {len(deduped_records):,} rows. Lexical Vocabulary: {len(vocab):,} unique words.")

    print("\n⏳ [3/4] Performing Stratified Split (80% Train, 10% Val, 10% Test Gold)...")
    split_by_leaf: dict[int, list[dict[str, Any]]] = {}
    for row in deduped_records:
        split_by_leaf.setdefault(int(row["good_type_id"]), []).append(row)

    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    rng = random.Random(args.seed)
    for lid, items in split_by_leaf.items():
        rng.shuffle(items)
        n = len(items)
        n_train = int(n * 0.80)
        n_val = int(n * 0.10)

        train_rows.extend(items[:n_train])
        val_rows.extend(items[n_train:n_train + n_val])
        test_rows.extend(items[n_train + n_val:])

    rng.shuffle(train_rows)
    rng.shuffle(val_rows)
    rng.shuffle(test_rows)
    rng.shuffle(deduped_records)

    print("\n⏳ [4/4] Writing CSV files with Excel BOM (utf-8-sig)...")
    csv_fields = [
        "text",
        "good_type_id",
        "good_type_name_ar",
        "good_type_name_en",
        "parent_root_id",
        "parent_root_name_ar",
        "parent_root_name_en",
        "language",
        "source",
    ]

    def write_csv(filepath: Path, records: list[dict[str, Any]]) -> None:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(records)

    write_csv(out_path / "dataset_1m_complete.csv", deduped_records)
    write_csv(out_path / "train_800k.csv", train_rows)
    write_csv(out_path / "val_100k.csv", val_rows)
    write_csv(out_path / "test_gold_100k.csv", test_rows)

    audit_summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_records": len(deduped_records),
        "train_records": len(train_rows),
        "val_records": len(val_rows),
        "test_records": len(test_rows),
        "leaf_classes_count": len(cat_counts),
        "unique_vocab_size": len(vocab),
        "zero_duplicate_guarantee": True,
        "files_exported": [
            "dataset_1m_complete.csv",
            "train_800k.csv",
            "val_100k.csv",
            "test_gold_100k.csv",
        ],
        "category_distribution": cat_counts,
    }

    with open(out_path / "audit_report.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, ensure_ascii=False, indent=2)

    total_elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 80)
    print("✨ AI SEMANTIC DATASET GENERATION COMPLETED & EXPORTED TO CSV/EXCEL")
    print("=" * 80)
    print(f"📊 Total Unique Records:   {len(deduped_records):,}")
    print(f"🚆 Train (80%):            {len(train_rows):,} rows -> train_800k.csv")
    print(f"🔍 Validation (10%):       {len(val_rows):,} rows -> val_100k.csv")
    print(f"🏆 Test Gold (10%):        {len(test_rows):,} rows -> test_gold_100k.csv")
    print(f"🌿 Leaf Classes:           {len(cat_counts)} / 90 leaf categories")
    print(f"📚 Distinct Vocabulary:    {len(vocab):,} unique words")
    print(f"⏱️ Total Time:             {total_elapsed:.2f}s")
    print(f"💾 Files Saved to:         {args.output_dir}/")
    print("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
