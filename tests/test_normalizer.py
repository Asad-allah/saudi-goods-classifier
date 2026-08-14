from app.nlp.language import detect_language
from app.nlp.lexical import token_variants
from app.nlp.normalizer import compact_text, normalize_text


def test_arabic_normalization_is_conservative() -> None:
    assert normalize_text("مــواد غِذائيّة") == "مواد غذائيه"
    assert normalize_text("عمود كهرباء") == "عمود كهربا"


def test_brand_spacing_can_be_compacted() -> None:
    normalized = normalize_text("كيت كات")
    assert normalized == "كيت كات"
    assert compact_text(normalized) == "كيتكات"


def test_long_repeated_letters_are_collapsed_before_matching() -> None:
    assert normalize_text("بطاااااطس") == "بطاطس"
    assert normalize_text("zzzzzz") == "z"


def test_light_lexical_variants_are_generated_for_both_catalog_and_input_forms() -> None:
    assert "بسكوت" in token_variants("بسكوته")
    assert "بسكوت" in token_variants("بسكوت")
    assert "كرتون" in token_variants("كرتونات")


def test_language_detection() -> None:
    assert detect_language("مواد غذائية") == "AR"
    assert detect_language("kit kat") == "EN"
    assert detect_language("كيت kat") == "MIXED"
    assert detect_language("チョコ") == "OTHER"
