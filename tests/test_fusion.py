from app.search.fusion import fuse_hits
from app.search.models import CandidateHit


def _hit(root_id: int, score: float, rank: int, method: str) -> CandidateHit:
    return CandidateHit(
        root_good_type_id=root_id,
        source_good_type_id=root_id,
        rank=rank,
        score=score,
        method=method,
        matched_term=f"term-{root_id}-{rank}",
    )


def test_high_confidence_semantic_evidence_beats_many_weak_fuzzy_hits() -> None:
    candidates = fuse_hits(
        [
            _hit(12, 0.72, 1, "FUZZY"),
            _hit(12, 0.70, 2, "FUZZY"),
            _hit(12, 0.69, 3, "FUZZY"),
            _hit(131, 0.86, 1, "SEMANTIC"),
        ]
    )

    assert candidates[0].root_good_type_id == 131
    assert candidates[0].method_evidence[0].method == "SEMANTIC"
    assert candidates[0].method_evidence[0].score == 0.86


def test_weak_generic_fuzzy_evidence_cannot_overturn_a_stronger_semantic_root() -> None:
    """A generic shared word must remain retrieval evidence, not a decisive vote.

    This mirrors a description such as "trash bags": a low fuzzy match to a
    food term containing "bags" must not outrank the semantically stronger
    waste category.
    """
    candidates = fuse_hits(
        [
            _hit(12, 0.6632, 6, "FUZZY"),
            _hit(12, 0.8741, 7, "SEMANTIC"),
            _hit(141, 0.8993, 1, "SEMANTIC"),
        ]
    )

    assert candidates[0].root_good_type_id == 141
    assert candidates[0].methods == ("SEMANTIC",)
