from pathlib import Path

import pytest

from app.catalog.importer import build_catalog, load_catalog_from_sql
from app.catalog.models import GoodType


def _fixture_catalog():
    return build_catalog(
        [
            GoodType(12, "مواد غذائية", "Food Items", (), None),
            GoodType(14, "سلع جافة", "Dry FMCG", ("بسكويت", "كيت كات"), 12),
            GoodType(10, "منتجات بترولية", "Petroleum Products", (), None),
            GoodType(19, "95بنزين", "Petrol 95", ("بنزين",), 10),
        ],
        source_sha256="fixture",
        version="test",
    )


def test_build_catalog_rolls_child_terms_up_to_root() -> None:
    catalog = _fixture_catalog()
    assert catalog.root_count == 2
    assert catalog.good_type_count == 4
    assert catalog.selectable_count == 2
    assert catalog.is_selectable(14) is True
    assert catalog.is_selectable(12) is False
    kitkat = [term for term in catalog.terms if term.normalized_term == "كيت كات"]
    assert kitkat
    assert kitkat[0].root_good_type_id == 12
    assert kitkat[0].source_good_type_id == 14


def test_catalog_import_ignores_null_common_names_and_unreviewed_english_names() -> None:
    catalog = build_catalog(
        [
            GoodType(131, "الإلكترونيات", "Reinforcing", (None, "لابتوب"), None),  # type: ignore[arg-type]
        ],
        source_sha256="fixture",
        version="test",
    )

    assert all(term.raw_term != "None" for term in catalog.terms)
    assert all(term.raw_term != "Reinforcing" for term in catalog.terms)
    assert any(term.raw_term == "لابتوب" for term in catalog.terms)


def test_real_sub_db_has_expected_root_count_when_available() -> None:
    path = Path.home() / "Downloads" / "Telegram Desktop" / "sub_db.sql"
    if not path.exists():
        pytest.skip("sub_db.sql is not available on this machine")
    catalog = load_catalog_from_sql(path)
    assert catalog.root_count == 37
    assert catalog.good_type_count == 103
    assert catalog.selectable_count == 90
    assert catalog.root(12).name_ar == "مواد غذائية"
    assert all(term.root_good_type_id in catalog.roots for term in catalog.terms)
    assert all(term.source_good_type_id in catalog.good_types for term in catalog.terms)
