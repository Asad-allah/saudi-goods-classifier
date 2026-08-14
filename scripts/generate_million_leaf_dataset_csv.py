#!/usr/bin/env python3
"""Streaming generator for 1,000,000 unique bilingual records distributed across all 90 LEAF categories."""

from __future__ import annotations
import argparse
import csv
import json
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from app.data_engine.leaf_ontology import LEAF_ONTOLOGY, LeafSpec
from app.data_engine.vocabularies import (
    PACKAGING_CONTAINERS_AR,
    PACKAGING_CONTAINERS_EN,
    QUANTITY_PREFIXES_AR,
    QUANTITY_PREFIXES_EN,
    PREFIXES_AR,
    PREFIXES_EN,
    MODIFIERS_AR,
    MODIFIERS_EN,
    apply_realistic_noise,
)
from app.nlp.normalizer import normalize_text


def generate_leaf_samples(spec: LeafSpec, target_count: int, rng: random.Random) -> list[str]:
    """Generates unique, rich bilingual samples for a specific leaf category."""
    results: set[str] = set()
    attempts = 0
    max_attempts = target_count * 30

    while len(results) < target_count and attempts < max_attempts:
        attempts += 1
        lang_mode = rng.choices(["ar", "en", "mixed"], weights=[60, 25, 15], k=1)[0]
        archetype = rng.choices(
            ["packaging", "brand_noun", "dialect_prefix", "spec_modifier", "compound"],
            weights=[30, 25, 20, 15, 10],
            k=1,
        )[0]

        if lang_mode == "ar":
            noun = rng.choice(spec.core_nouns_ar)
            brand = rng.choice(spec.brands_ar) if spec.brands_ar else ""
            packaging = rng.choice(spec.packaging_ar) if spec.packaging_ar else rng.choice(PACKAGING_CONTAINERS_AR)
            qty = rng.choice(QUANTITY_PREFIXES_AR)
            prefix = rng.choice(PREFIXES_AR)
            modifier = rng.choice(MODIFIERS_AR)

            if archetype == "packaging":
                parts = [qty, packaging, noun]
                if brand and rng.random() > 0.5:
                    parts.append(brand)
                text = " ".join(p for p in parts if p)
            elif archetype == "brand_noun":
                parts = [noun, brand]
                if rng.random() > 0.4:
                    parts.append(modifier)
                text = " ".join(p for p in parts if p)
            elif archetype == "dialect_prefix":
                parts = [prefix, noun]
                if rng.random() > 0.4:
                    parts.append(modifier)
                text = " ".join(p for p in parts if p)
            elif archetype == "spec_modifier":
                parts = [noun, rng.choice(spec.specs_ar), modifier]
                text = " ".join(p for p in parts if p)
            else: # compound
                noun2 = rng.choice(spec.core_nouns_ar)
                parts = [qty, packaging, noun, "و", noun2]
                text = " ".join(p for p in parts if p)

            final_text = apply_realistic_noise(text, noise_probability=0.18)

        elif lang_mode == "en":
            noun_en = rng.choice(spec.core_nouns_en)
            brand_en = rng.choice(spec.brands_en) if spec.brands_en else ""
            packaging_en = rng.choice(spec.packaging_en) if spec.packaging_en else rng.choice(PACKAGING_CONTAINERS_EN)
            qty_en = rng.choice(QUANTITY_PREFIXES_EN)
            prefix_en = rng.choice(PREFIXES_EN)
            modifier_en = rng.choice(MODIFIERS_EN)

            if archetype == "packaging":
                parts = [qty_en, packaging_en, "of", noun_en]
                if brand_en and rng.random() > 0.5:
                    parts.append(f"({brand_en})")
                text = " ".join(p for p in parts if p)
            elif archetype == "brand_noun":
                parts = [brand_en, noun_en]
                if rng.random() > 0.4:
                    parts.append(modifier_en)
                text = " ".join(p for p in parts if p)
            elif archetype == "dialect_prefix":
                parts = [prefix_en, noun_en]
                if rng.random() > 0.4:
                    parts.append(modifier_en)
                text = " ".join(p for p in parts if p)
            elif archetype == "spec_modifier":
                parts = [noun_en, rng.choice(spec.specs_en), modifier_en]
                text = " ".join(p for p in parts if p)
            else: # compound
                noun_en2 = rng.choice(spec.core_nouns_en)
                parts = [qty_en, packaging_en, "of", noun_en, "and", noun_en2]
                text = " ".join(p for p in parts if p)

            final_text = text

        else: # Mixed
            noun_ar = rng.choice(spec.core_nouns_ar)
            brand_en = rng.choice(spec.brands_en) if spec.brands_en else ""
            packaging_ar = rng.choice(spec.packaging_ar) if spec.packaging_ar else rng.choice(PACKAGING_CONTAINERS_AR)
            qty_ar = rng.choice(QUANTITY_PREFIXES_AR)
            prefix_ar = rng.choice(PREFIXES_AR)

            parts = [prefix_ar, qty_ar, packaging_ar, noun_ar]
            if brand_en:
                parts.append(brand_en)
            text = " ".join(p for p in parts if p)
            final_text = text

        if len(final_text.strip()) >= 4:
            results.add(final_text.strip())

    return sorted(results)[:target_count]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate 1,000,000 unique records distributed across all 90 LEAF categories."
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
        default="storage/training/million_leaf_dataset",
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

    print("=" * 75)
    print(f"🚀 MASSIVE 1-MILLION DATASET ON ALL 90 LEAF CATEGORIES (NO ROOT ROLLUP)")
    print("=" * 75)
    print(f"🎯 Target Total:        {total_target:,} records ({target_per_leaf:,} per leaf x {num_leaves} leaves)")
    print(f"🌿 Target Classes:      {num_leaves} LEAF Categories (Direct leaf classification)")
    print(f"🌐 Languages:           Arabic (~60%), English (~25%), Mixed (~15%)")
    print(f"📁 Output Directory:    {args.output_dir}/")
    print(f"💾 File Format:         CSV (UTF-8-SIG with BOM for Excel & Pandas)")
    print("=" * 75 + "\n")

    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    start_time = time.perf_counter()
    all_clean_records: list[dict[str, Any]] = []

    print("⏳ [1/4] Generating distinct bilingual samples for all 90 leaf categories...")
    for idx, (leaf_id, spec) in enumerate(LEAF_ONTOLOGY.items(), start=1):
        cat_start = time.perf_counter()
        samples = generate_leaf_samples(spec, target_count=target_per_leaf, rng=rng)

        for text in samples:
            all_clean_records.append({
                "text": text,
                "good_type_id": leaf_id,
                "good_type_name_ar": spec.name_ar,
                "good_type_name_en": spec.name_en,
                "parent_root_id": spec.parent_id if spec.parent_id else leaf_id,
                "parent_root_name_ar": spec.parent_name_ar,
                "parent_root_name_en": spec.parent_name_en,
                "language": "AR" if any("\u0600" <= c <= "\u06ff" for c in text) and not any(c.isascii() and c.isalpha() for c in text) else ("EN" if all(not ("\u0600" <= c <= "\u06ff") for c in text) else "MIXED"),
                "source": "saudi_leaf_gold_generator",
            })

        cat_elapsed = time.perf_counter() - cat_start
        if idx % 10 == 0 or idx == num_leaves:
            print(f"  [{idx:02d}/{num_leaves}] Leaf {leaf_id:3d} ({spec.name_ar[:25]:25s}) -> {len(samples):,d} rows (Total generated: {len(all_clean_records):,d})")

    print(f"\n⏳ [2/4] Validating uniqueness and cross-leaf integrity across {len(all_clean_records):,} rows...")
    seen_texts: set[str] = set()
    deduped_records: list[dict[str, Any]] = []
    vocab: set[str] = set()
    category_counts: dict[int, int] = {}

    for row in all_clean_records:
        norm = normalize_text(str(row["text"]))
        if norm in seen_texts:
            continue
        seen_texts.add(norm)
        deduped_records.append(row)
        category_counts[row["good_type_id"]] = category_counts.get(row["good_type_id"], 0) + 1
        for w in norm.split():
            vocab.add(w)

    print(f"  Deduped total: {len(deduped_records):,} unique rows. Vocab size: {len(vocab):,} words.")

    print("\n⏳ [3/4] Performing Stratified Split (80% Train, 10% Val, 10% Test Gold)...")
    split_by_leaf: dict[int, list[dict[str, Any]]] = {}
    for row in deduped_records:
        split_by_leaf.setdefault(int(row["good_type_id"]), []).append(row)

    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

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

    print("\n⏳ [4/4] Exporting to CSV (UTF-8 with BOM for Excel & Pandas compatibility)...")
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

    write_csv(out_path / "dataset_1m_leaf_complete.csv", deduped_records)
    write_csv(out_path / "train_800k_leaf.csv", train_rows)
    write_csv(out_path / "val_100k_leaf.csv", val_rows)
    write_csv(out_path / "test_gold_100k_leaf.csv", test_rows)

    audit_summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_records": len(deduped_records),
        "train_records": len(train_rows),
        "val_records": len(val_rows),
        "test_records": len(test_rows),
        "leaf_classes_count": len(category_counts),
        "unique_vocab_size": len(vocab),
        "files_exported": [
            "dataset_1m_leaf_complete.csv",
            "train_800k_leaf.csv",
            "val_100k_leaf.csv",
            "test_gold_100k_leaf.csv",
        ],
        "category_distribution": category_counts,
    }

    with open(out_path / "audit_report_leaf_1m.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, ensure_ascii=False, indent=2)

    total_elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 75)
    print("🎉 1-MILLION LEAF DATASET COMPLETED & SAVED TO CSV / EXCEL")
    print("=" * 75)
    print(f"📊 Total Records:          {len(deduped_records):,}")
    print(f"🚆 Train Set (80%):        {len(train_rows):,} rows -> train_800k_leaf.csv")
    print(f"🔍 Val Set (10%):          {len(val_rows):,} rows -> val_100k_leaf.csv")
    print(f"🏆 Test Gold Set (10%):    {len(test_rows):,} rows -> test_gold_100k_leaf.csv")
    print(f"🌿 Leaf Classes Covered:   {len(category_counts)} / 90 leaf categories")
    print(f"📚 Unique Words Vocab:     {len(vocab):,} words")
    print(f"⏱️ Total Execution Time:   {total_elapsed:.2f}s")
    print(f"💾 Files Saved in:         {args.output_dir}/")
    print("=" * 75 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
