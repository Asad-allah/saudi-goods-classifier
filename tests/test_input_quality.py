import pytest

from app.catalog.importer import build_catalog
from app.catalog.models import GoodType
from app.nlp.input_quality import (
    InputNeedsContext,
    InputNotMeaningful,
    InputQualityGate,
)


def _quality_gate() -> InputQualityGate:
    catalog = build_catalog(
        [
            GoodType(
                12,
                "مواد غذائية",
                "Food Items",
                ("سكر", "حليب", "كيت كات", "بسكوت"),
                None,
            ),
            GoodType(34, "مواد البناء", "Building Items", ("حديد", "بنزين"), None),
            GoodType(131, "الإلكترونيات", "Electronics", ("تلفزيون",), None),
        ],
        source_sha256="fixture",
        version="test",
    )
    return InputQualityGate(catalog)


@pytest.mark.parametrize(
    "text",
    [
        "123456",
        "3m",
        "رز",
        "سسسسسس",
        "سسسسح",
        "zzzzzz",
        "صثبسيؤشص",
        "xqjkpw",
        "qwer asdf",
        "و",
    ],
)
def test_quality_gate_rejects_meaningless_input(text: str) -> None:
    with pytest.raises(InputNotMeaningful):
        _quality_gate().require_meaningful(text)


@pytest.mark.parametrize(
    "text",
    [
        "حديد",
        "سكر",
        "تلفزيون ذكي 65 بوصة",
        "kit kat",
        "xenova kitchen blender",
        "بنزين و كيت كات",
        "شحاطة بلاستيك",
    ],
)
def test_quality_gate_accepts_meaningful_goods_descriptions(text: str) -> None:
    _quality_gate().require_meaningful(text)


@pytest.mark.parametrize("text", ["غسالة سامسونج", "غساله سامسونج"])
def test_quality_gate_accepts_common_arabic_goods_words_outside_catalog(
    text: str,
) -> None:
    _quality_gate().require_meaningful(text)


def test_quality_gate_requires_context_for_a_single_unknown_brand_like_word() -> None:
    with pytest.raises(InputNeedsContext):
        _quality_gate().require_meaningful("qazmori")


def test_quality_gate_accepts_a_strong_typo_of_a_catalog_goods_word() -> None:
    _quality_gate().require_meaningful("بسكوتة سنيكرز")


def test_quality_gate_accepts_natural_three_letter_words_with_repeated_letters() -> None:
    _quality_gate().require_meaningful("باب خشب")


@pytest.mark.parametrize("text", ["سسسسس خشب", "رز خشب", "qwer تلفزيون"])
def test_quality_gate_accepts_phrase_when_one_content_word_is_meaningful(
    text: str,
) -> None:
    _quality_gate().require_meaningful(text)
