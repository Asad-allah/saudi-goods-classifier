from app.catalog.importer import build_catalog
from app.catalog.models import GoodType
from app.search.fuzzy import FuzzyRetriever


def _retriever() -> FuzzyRetriever:
    catalog = build_catalog(
        [
            GoodType(12, "مواد غذائية", "Food Items", ("بسكوت", "كياس دقيق"), None),
            GoodType(34, "مواد البناء", "Building Items", ("كياس سمنت",), None),
        ],
        source_sha256="fixture",
        version="test",
    )
    return FuzzyRetriever(catalog.terms)


def test_light_lexical_variant_strengthens_a_specific_catalog_goods_word() -> None:
    hits = _retriever().search("بسكوتة سنيكرز", top_k=10)

    biscuit_hit = next(hit for hit in hits if hit.matched_term == "بسكوت")
    assert biscuit_hit.score == 0.98


def test_shared_generic_token_does_not_become_strong_fuzzy_evidence() -> None:
    hits = _retriever().search("كياس زبالة", top_k=10)

    bag_hits = [hit for hit in hits if hit.matched_term in {"كياس دقيق", "كياس سمنت"}]
    assert bag_hits
    assert all(hit.score < 0.98 for hit in bag_hits)
