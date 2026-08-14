from app.catalog.importer import build_catalog
from app.catalog.models import GoodType
from app.classifier.service import RootCategoryClassifier


def _classifier(*, input_validation_enabled: bool = True) -> RootCategoryClassifier:
    catalog = build_catalog(
        [
            GoodType(12, "مواد غذائية", "Food Items", (), None),
            GoodType(
                14,
                "سلع جافة",
                "Dry FMCG",
                ("بسكويت", "بسكوت", "كيت كات", "شوكولاته", "بطاطس"),
                12,
            ),
            GoodType(15, "سلع مبردة", "Chilled FMCG", ("حليب",), 12),
            GoodType(10, "منتجات بترولية", "Petroleum Products", (), None),
            GoodType(19, "95بنزين", "Petrol 95", ("بنزين",), 10),
            GoodType(11, "حيوانات حية", "Live Animals", (), None),
            GoodType(123, "طيور", "Birds", ("بط",), 11),
            GoodType(34, "مواد البناء", "Building Items", (), None),
            GoodType(54, "أبواب خشب", "Wooden Doors", ("باب خشب",), 34),
            GoodType(159, "مولدات الكهرباء", "Generators", ("مولد كهرباء",), None),
            GoodType(131, "الإلكترونيات", "Electronics", ("لابتوب",), None),
        ],
        source_sha256="fixture",
        version="test",
    )
    return RootCategoryClassifier(
        catalog,
        input_validation_enabled=input_validation_enabled,
    )


def test_exact_alias_returns_root_category() -> None:
    result = _classifier().classify(request_id="1", text="كيت كات")
    assert result.top_category is not None
    assert result.top_category.good_type_id == 14
    assert result.top_category.root_good_type_id == 12
    assert result.reason == "EXACT"
    assert result.requires_review is False


def test_fuzzy_typo_returns_food_with_review_flag() -> None:
    result = _classifier().classify(request_id="2", text="مواد غزائيه")
    assert result.top_category is None
    assert result.requires_review is True
    assert result.reason in {"EMBEDDING_UNAVAILABLE", "LOW_EVIDENCE"}


def test_fuzzy_catalog_anchor_allows_brand_with_a_goods_word_typo() -> None:
    result = _classifier().classify(request_id="snickers", text="بسكوتة سنيكرز")

    assert result.top_category is not None
    assert result.top_category.good_type_id == 14
    assert result.top_category.root_good_type_id == 12


def test_unsupported_language_keeps_candidate_but_requires_review() -> None:
    result = _classifier().classify(request_id="3", text="チョコ")
    assert result.top_category is None
    assert result.requires_review is True
    assert result.reason == "UNSUPPORTED_LANGUAGE"


def test_multi_category_marks_review() -> None:
    result = _classifier().classify(request_id="4", text="بنزين و كيت كات")
    assert result.requires_review is True
    assert result.reason == "MULTI_CATEGORY"


def test_disabled_input_validation_sends_repeated_text_to_retrieval() -> None:
    result = _classifier(input_validation_enabled=False).classify(
        request_id="validation-off",
        text="سسسسسس",
    )

    assert result.request_id == "validation-off"
    assert result.normalized_text == "س"
    assert result.top_category is None


def test_repeated_potato_does_not_match_short_bird_alias() -> None:
    result = _classifier(input_validation_enabled=False).classify(
        request_id="potato",
        text="بطاااااطس",
    )

    assert result.top_category is not None
    assert result.top_category.good_type_id == 14
    assert all(candidate.good_type_id != 123 for candidate in result.alternatives[:1])


def test_unknown_phosphate_abstains_instead_of_forcing_food() -> None:
    result = _classifier(input_validation_enabled=False).classify(
        request_id="phosphate",
        text="فوسفات",
    )

    assert result.top_category is None
    assert result.requires_review is True
    assert result.reason in {"LOW_EVIDENCE", "EMBEDDING_UNAVAILABLE"}


def test_lamp_does_not_become_generator_by_fuzzy_only() -> None:
    result = _classifier(input_validation_enabled=False).classify(
        request_id="lamp",
        text="لمبة كهربائية",
    )

    assert result.top_category is None
    assert result.requires_review is True


def test_exact_leaf_for_wooden_door_returns_child_not_root() -> None:
    result = _classifier().classify(request_id="door", text="باب خشب")

    assert result.top_category is not None
    assert result.top_category.good_type_id == 54
    assert result.top_category.root_good_type_id == 34
