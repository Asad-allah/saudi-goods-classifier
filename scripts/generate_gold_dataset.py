#!/usr/bin/env python3
"""CLI for industrial dataset generation, disambiguation, and export."""

from __future__ import annotations
import argparse
import sys
import time
from app.data_engine.pipeline import DatasetPipeline, DatasetConfig


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate industrial-grade, zero-conflict dataset for Saudi goods classification."
    )
    parser.add_argument(
        "--target-per-category",
        type=int,
        default=1000,
        help="Target number of unique verified samples per root category (default: 1000).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="storage/training/gold_dataset",
        help="Output directory for generated datasets and audit report.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )

    args = parser.parse_args()

    print(f"🚀 Starting Industrial Dataset Generation Pipeline...")
    print(f"🎯 Target: {args.target_per_category} samples/root across 37 categories (Total ~{args.target_per_category * 37:,})")
    print(f"📁 Output Directory: {args.output_dir}")

    config = DatasetConfig(
        target_per_category=args.target_per_category,
        output_dir=args.output_dir,
        seed=args.seed,
    )

    start_time = time.perf_counter()
    pipeline = DatasetPipeline(config)
    report = pipeline.run()
    elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 60)
    print("✨ DATASET GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"📊 Total Samples:      {report['total_samples']:,}")
    print(f"🚆 Train Samples:      {report['train_samples']:,} (80%)")
    print(f"🔍 Val Samples:        {report['val_samples']:,} (10%)")
    print(f"🏆 Test Gold Samples:  {report['test_samples']:,} (10%)")
    print(f"🏛️ Categories Covered: {report['categories_covered']} / 37")
    print(f"📚 Lexical Vocab Size: {report['lexical_vocab_size']:,} unique words")
    print(f"🛡️ Conflict Rate:      {report['conflict_rate_pct']:.4f}% (Zero Conflict: {report['is_zero_conflict']})")
    print(f"⏱️ Time Elapsed:       {elapsed:.2f}s")
    print(f"💾 Files Saved to:     {args.output_dir}/")
    print("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
