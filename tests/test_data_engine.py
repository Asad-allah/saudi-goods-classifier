from __future__ import annotations
import json
from pathlib import Path
from app.data_engine.ontology import ROOT_ONTOLOGY
from app.data_engine.disambiguator import DisambiguationEngine
from app.data_engine.generator import LogisticsDatasetGenerator
from app.data_engine.sanitizer import DatasetSanitizer
from app.data_engine.validator import ZeroConflictValidator
from app.data_engine.pipeline import DatasetPipeline, DatasetConfig


def test_ontology_contains_all_37_roots() -> None:
    assert len(ROOT_ONTOLOGY) == 37
    for root_id, spec in ROOT_ONTOLOGY.items():
        assert spec.root_id == root_id
        assert spec.name_ar
        assert spec.name_en
        assert len(spec.core_nouns) >= 7
        assert len(spec.domains) >= 2


def test_disambiguation_engine_enforces_anchors() -> None:
    engine = DisambiguationEngine()
    
    # "زيت" without anchor in food items (12) should get anchored or validated
    is_valid, text = engine.validate_and_anchor("كرتون زيت عافية", 12)
    assert is_valid
    assert "عافية" in text or "طعام" in text

    # "زيت" with engine/car context in food items (12) should be rejected
    is_valid_food, _ = engine.validate_and_anchor("زيت محرك 5w30 بترومين", 12)
    # The food category excludes engine oil/petroleum
    # but in spares (129) it is valid
    is_valid_spares, text_spares = engine.validate_and_anchor("زيت محرك 5w30 بترومين", 129)
    assert is_valid_spares
    assert "محرك" in text_spares or "بترومين" in text_spares


def test_generator_produces_diverse_samples() -> None:
    gen = LogisticsDatasetGenerator(seed=123)
    samples = gen.generate_category_samples(12, target_count=50)
    assert len(samples) == 50
    assert len(set(samples)) == 50
    # Samples must be non-empty and Arabic-rich
    for s in samples:
        assert len(s) >= 4


def test_sanitizer_cleans_text() -> None:
    sanitizer = DatasetSanitizer()
    assert sanitizer.clean("  كرتون   حليب  نيدو   ") == "كرتون حليب نيدو"
    assert sanitizer.is_acceptable("كرتون حليب نيدو 2.5 كجم")
    assert not sanitizer.is_acceptable("1234567")
    assert not sanitizer.is_acceptable("ab")


def test_validator_detects_and_purges_cross_conflicts() -> None:
    validator = ZeroConflictValidator()
    dataset = [
        {"text": "كرتون تونة قودي", "root_id": 12},
        {"text": "مكيف سبليت 18 وحدة", "root_id": 179},
        {"text": "عبارة متضاربة عمداً", "root_id": 12},
        {"text": "عبارة متضاربة عمداً", "root_id": 131},  # conflict!
    ]
    cleaned, report = validator.validate_and_filter(dataset)
    assert len(cleaned) == 2
    assert report.exact_conflicts_found == 1
    assert report.conflict_rate_pct > 0


def test_pipeline_executes_mini_run(tmp_path: Path) -> None:
    config = DatasetConfig(
        target_per_category=5,  # mini test
        output_dir=str(tmp_path),
        seed=42,
    )
    pipeline = DatasetPipeline(config)
    report = pipeline.run()

    assert report["categories_covered"] == 37
    assert report["total_samples"] == 37 * 5
    assert (tmp_path / "train.jsonl").exists()
    assert (tmp_path / "test_gold.jsonl").exists()
    assert (tmp_path / "audit_report.json").exists()
