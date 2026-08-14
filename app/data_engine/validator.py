"""Zero-conflict verification and cross-category collision scanner."""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from app.nlp.normalizer import normalize_text, compact_text


@dataclass(frozen=True)
class ValidationReport:
    total_samples: int
    category_counts: dict[int, int]
    exact_conflicts_found: int
    conflict_rate_pct: float
    lexical_vocab_size: int
    is_zero_conflict: bool


class ZeroConflictValidator:
    """Validates complete dataset integrity and purges cross-category collisions."""

    def __init__(self) -> None:
        pass

    def validate_and_filter(
        self,
        dataset: list[dict[str, int | str]],
    ) -> tuple[list[dict[str, int | str]], ValidationReport]:
        """
        Scans all records for cross-root collisions and purges ambiguous duplicates.
        Ensures strict single-label truth.
        """
        # Map normalized string -> set of root_ids
        norm_to_roots: dict[str, set[int]] = defaultdict(set)
        for row in dataset:
            text = str(row["text"])
            root_id = int(row["root_id"])
            norm = normalize_text(text)
            norm_to_roots[norm].add(root_id)

        conflicted_norms = {norm for norm, roots in norm_to_roots.items() if len(roots) > 1}

        clean_dataset: list[dict[str, int | str]] = []
        seen_exact: set[tuple[int, str]] = set()
        vocab: set[str] = set()
        category_counts: dict[int, int] = defaultdict(int)

        for row in dataset:
            text = str(row["text"])
            root_id = int(row["root_id"])
            norm = normalize_text(text)

            if norm in conflicted_norms:
                continue

            pair_key = (root_id, norm)
            if pair_key in seen_exact:
                continue
            seen_exact.add(pair_key)

            clean_dataset.append(row)
            category_counts[root_id] += 1
            for word in norm.split():
                vocab.add(word)

        total_samples = len(clean_dataset)
        conflicts_count = len(conflicted_norms)
        conflict_rate = (conflicts_count / max(1, len(dataset))) * 100

        report = ValidationReport(
            total_samples=total_samples,
            category_counts=dict(category_counts),
            exact_conflicts_found=conflicts_count,
            conflict_rate_pct=conflict_rate,
            lexical_vocab_size=len(vocab),
            is_zero_conflict=(conflicts_count == 0),
        )

        return clean_dataset, report
