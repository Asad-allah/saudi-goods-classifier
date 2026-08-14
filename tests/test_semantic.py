from app.catalog.importer import build_catalog
from app.catalog.models import GoodType
from app.search.semantic import (
    _embedding_cache_path,
    _model_version_label,
    build_semantic_documents,
)


def test_semantic_documents_include_root_context_from_catalog_only() -> None:
    catalog = build_catalog(
        [
            GoodType(12, "مواد غذائية", "Food Items", (), None),
            GoodType(14, "سلع جافة", "Dry FMCG", ("بسكويت",), 12),
        ],
        source_sha256="fixture",
        version="test",
    )

    documents = build_semantic_documents(catalog)

    biscuit_document = next(item for item in documents if item.matched_term == "بسكويت")
    assert biscuit_document.root_good_type_id == 12
    assert biscuit_document.source_good_type_id == 14
    assert "سلع جافة" in biscuit_document.text
    assert "مواد غذائية" in biscuit_document.text
    assert "Food Items" not in biscuit_document.text
    assert all("كيت كات" not in item.text for item in documents)


def test_semantic_documents_add_one_generated_profile_per_root() -> None:
    catalog = build_catalog(
        [
            GoodType(12, "مواد غذائية", "Food Items", (), None),
            GoodType(14, "سلع جافة", "Dry FMCG", ("بسكويت", "شوكولاتة"), 12),
        ],
        source_sha256="fixture",
        version="test",
    )

    documents = build_semantic_documents(catalog)

    profiles = [item for item in documents if item.source_type == "GOOD_TYPE_PROFILE"]
    assert len(profiles) == 1
    assert profiles[0].root_good_type_id == 12
    assert profiles[0].source_good_type_id == 14
    assert "بسكويت" in profiles[0].text
    assert "شوكولاتة" in profiles[0].text


def test_root_profile_limits_examples_to_avoid_model_input_truncation() -> None:
    common_names = tuple(f"term-{index}" for index in range(75))
    catalog = build_catalog(
        [GoodType(12, "مواد غذائية", "Food Items", common_names, None)],
        source_sha256="fixture",
        version="test",
    )

    profile = next(
        item
        for item in build_semantic_documents(catalog)
        if item.source_type == "GOOD_TYPE_PROFILE"
    )

    assert "term-67" in profile.text
    assert "term-68" not in profile.text


def test_semantic_documents_add_a_clean_good_type_label_for_zero_shot_matching() -> None:
    catalog = build_catalog(
        [GoodType(12, "مواد غذائية", "Food Items", (), None)],
        source_sha256="fixture",
        version="test",
    )

    documents = build_semantic_documents(catalog)

    labels = [item for item in documents if item.source_type == "GOOD_TYPE_LABEL"]
    assert len(labels) == 1
    assert labels[0].matched_term == "مواد غذائية"
    assert labels[0].text.endswith("Main goods group: مواد غذائية.")


def test_embedding_cache_path_changes_when_catalog_or_model_changes(tmp_path) -> None:
    catalog = build_catalog(
        [GoodType(12, "مواد غذائية", "Food Items", (), None)],
        source_sha256="fixture-a",
        version="test-a",
    )

    base = _embedding_cache_path(catalog, "model-a", tmp_path)
    changed_model = _embedding_cache_path(catalog, "model-b", tmp_path)
    changed_catalog = _embedding_cache_path(
        build_catalog(
            [GoodType(12, "مواد غذائية", "Food Items", (), None)],
            source_sha256="fixture-b",
            version="test-b",
        ),
        "model-a",
        tmp_path,
    )

    assert base.parent == tmp_path
    assert base != changed_model
    assert base != changed_catalog


def test_model_version_hides_the_absolute_local_model_path(tmp_path) -> None:
    local_model = tmp_path / "intfloat-multilingual-e5-small"
    local_model.mkdir()

    assert _model_version_label(str(local_model)) == "intfloat-multilingual-e5-small@local"
