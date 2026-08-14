"""End-to-end dataset generation, validation, splitting, and export pipeline."""

from __future__ import annotations
import json
import random
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.data_engine.ontology import ROOT_ONTOLOGY
from app.data_engine.generator import LogisticsDatasetGenerator
from app.data_engine.sanitizer import DatasetSanitizer
from app.data_engine.validator import ZeroConflictValidator, ValidationReport


@dataclass
class DatasetConfig:
    target_per_category: int = 1000
    train_ratio: float = 0.80
    val_ratio: float = 0.10
    test_ratio: float = 0.10
    seed: int = 42
    output_dir: str = "storage/training/gold_dataset"


class DatasetPipeline:
    """Industrial dataset orchestration pipeline."""

    def __init__(self, config: DatasetConfig | None = None) -> None:
        self.config = config or DatasetConfig()
        self.generator = LogisticsDatasetGenerator(seed=self.config.seed)
        self.sanitizer = DatasetSanitizer()
        self.validator = ZeroConflictValidator()

    def run(self) -> dict[str, Any]:
        """Runs full pipeline and returns audit report."""
        raw_records: list[dict[str, int | str]] = []

        # 1. Generation
        for root_id, spec in ROOT_ONTOLOGY.items():
            # Generate buffer to ensure we meet target after sanitization & conflict purging
            buffer_target = int(self.config.target_per_category * 1.15)
            samples = self.generator.generate_category_samples(root_id, target_count=buffer_target)

            for text in samples:
                if self.sanitizer.is_acceptable(text):
                    cleaned = self.sanitizer.clean(text)
                    raw_records.append({
                        "text": cleaned,
                        "root_id": root_id,
                        "root_name_ar": spec.name_ar,
                        "root_name_en": spec.name_en,
                        "source": "data_engine_gold_synthesizer",
                    })

        # 2. Validation & Zero-Conflict Filtering
        clean_dataset, report = self.validator.validate_and_filter(raw_records)

        # 3. Balance to exact target per category
        by_category: dict[int, list[dict[str, int | str]]] = {}
        for row in clean_dataset:
            rid = int(row["root_id"])
            by_category.setdefault(rid, []).append(row)

        rng = random.Random(self.config.seed)
        balanced_dataset: list[dict[str, int | str]] = []
        for rid, rows in by_category.items():
            rng.shuffle(rows)
            balanced_dataset.extend(rows[:self.config.target_per_category])

        # Re-validate balanced set
        final_dataset, final_report = self.validator.validate_and_filter(balanced_dataset)

        # 4. Stratified Split
        train_rows: list[dict[str, int | str]] = []
        val_rows: list[dict[str, int | str]] = []
        test_rows: list[dict[str, int | str]] = []

        split_by_cat: dict[int, list[dict[str, int | str]]] = {}
        for row in final_dataset:
            split_by_cat.setdefault(int(row["root_id"]), []).append(row)

        for rid, items in split_by_cat.items():
            n = len(items)
            n_train = int(n * self.config.train_ratio)
            n_val = int(n * self.config.val_ratio)

            train_rows.extend(items[:n_train])
            val_rows.extend(items[n_train:n_train + n_val])
            test_rows.extend(items[n_train + n_val:])

        # 5. Export
        out_path = Path(self.config.output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        _write_jsonl(out_path / "train.jsonl", train_rows)
        _write_jsonl(out_path / "val.jsonl", val_rows)
        _write_jsonl(out_path / "test_gold.jsonl", test_rows)
        _write_jsonl(out_path / "complete_dataset.jsonl", final_dataset)

        audit_summary = {
            "timestamp": datetime.now(UTC).isoformat(),
            "config": asdict(self.config),
            "total_samples": len(final_dataset),
            "train_samples": len(train_rows),
            "val_samples": len(val_rows),
            "test_samples": len(test_rows),
            "categories_covered": len(final_report.category_counts),
            "conflict_rate_pct": final_report.conflict_rate_pct,
            "lexical_vocab_size": final_report.lexical_vocab_size,
            "category_distribution": final_report.category_counts,
            "is_zero_conflict": final_report.is_zero_conflict,
        }

        with open(out_path / "audit_report.json", "w", encoding="utf-8") as f:
            json.dump(audit_summary, f, ensure_ascii=False, indent=2)

        return audit_summary


def _write_jsonl(filepath: Path, records: list[dict[str, Any]]) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
