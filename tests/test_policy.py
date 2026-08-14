from app.classifier.policy import decide
from app.search.fusion import RootCandidate
from app.search.models import CandidateHit


def _candidate(
    *,
    fuzzy: float,
    semantic: float,
    good_type_id: int = 12,
    score: float | None = None,
) -> RootCandidate:
    fuzzy_hit = CandidateHit(12, good_type_id, 1, fuzzy, "FUZZY", "generic bag term")
    semantic_hit = CandidateHit(12, good_type_id, 1, semantic, "SEMANTIC", "food bag term")
    return RootCandidate(
        root_good_type_id=12,
        source_good_type_id=good_type_id,
        rank=1,
        score=score if score is not None else fuzzy * 0.35 + semantic,
        methods=("FUZZY", "SEMANTIC"),
        method_evidence=(fuzzy_hit, semantic_hit),
        matched_terms=("generic bag term", "food bag term"),
        max_evidence=semantic,
        has_ambiguous_term=False,
    )


def test_weak_fuzzy_evidence_cannot_make_a_semantic_result_auto_accepted() -> None:
    requires_review, reason = decide(
        [_candidate(fuzzy=0.66, semantic=0.88)],
        language="AR",
        embedding_available=True,
    )

    assert requires_review is True
    assert reason == "LOW_EVIDENCE"


def test_strong_fuzzy_and_semantic_evidence_can_be_auto_accepted() -> None:
    requires_review, reason = decide(
        [_candidate(fuzzy=0.98, semantic=0.88)],
        language="AR",
        embedding_available=True,
    )

    assert requires_review is False
    assert reason == "HYBRID_STRONG"


def test_hybrid_evidence_needs_a_clear_margin_to_be_auto_accepted() -> None:
    top = _candidate(fuzzy=0.87, semantic=0.88, good_type_id=54, score=1.26)
    close = _candidate(fuzzy=0.87, semantic=0.87, good_type_id=159, score=1.245)

    requires_review, reason = decide(
        [top, close],
        language="AR",
        embedding_available=True,
    )

    assert requires_review is True
    assert reason == "AMBIGUOUS"


def test_clear_hybrid_margin_can_be_auto_accepted() -> None:
    top = _candidate(fuzzy=0.87, semantic=0.88, good_type_id=54, score=1.26)
    distant = _candidate(fuzzy=0.87, semantic=0.87, good_type_id=159, score=0.9)

    requires_review, reason = decide(
        [top, distant],
        language="AR",
        embedding_available=True,
    )

    assert requires_review is False
    assert reason == "HYBRID_STRONG"
