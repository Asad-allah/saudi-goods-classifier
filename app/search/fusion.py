from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from app.search.models import CandidateHit


@dataclass(frozen=True)
class RootCandidate:
    root_good_type_id: int
    source_good_type_id: int | None
    rank: int
    score: float
    methods: tuple[str, ...]
    method_evidence: tuple[CandidateHit, ...]
    matched_terms: tuple[str, ...]
    max_evidence: float
    has_ambiguous_term: bool

    @property
    def good_type_id(self) -> int:
        return self.source_good_type_id or self.root_good_type_id


_METHOD_WEIGHTS = {
    "EXACT": 2.0,
    "LEXICAL_VARIANT": 1.85,
    "FUZZY": 1.6,
    "SEMANTIC": 1.5,
}
_MIN_FUZZY_SCORE_FOR_SEMANTIC_FUSION = 0.75


def fuse_hits(hits: list[CandidateHit], *, top_k: int = 3) -> list[RootCandidate]:
    scores: dict[int, float] = defaultdict(float)
    methods: dict[int, set[str]] = defaultdict(set)
    matched_terms: dict[int, list[str]] = defaultdict(list)
    max_evidence: dict[int, float] = defaultdict(float)
    ambiguous: dict[int, bool] = defaultdict(bool)
    best_by_method: dict[int, dict[str, CandidateHit]] = defaultdict(dict)
    root_by_good_type: dict[int, int] = {}
    semantic_is_available = any(hit.method == "SEMANTIC" for hit in hits)

    for hit in hits:
        good_type_id = hit.source_good_type_id
        root_by_good_type[good_type_id] = hit.root_good_type_id
        methods[good_type_id].add(hit.method)
        if hit.matched_term not in matched_terms[good_type_id]:
            matched_terms[good_type_id].append(hit.matched_term)
        max_evidence[good_type_id] = max(max_evidence[good_type_id], hit.score)
        ambiguous[good_type_id] = (
            ambiguous[good_type_id]
            or hit.is_cross_good_type_ambiguous
            or hit.is_cross_root_ambiguous
        )
        best_hit = best_by_method[good_type_id].get(hit.method)
        if best_hit is None or hit.score > best_hit.score:
            best_by_method[good_type_id][hit.method] = hit

    for good_type_id, method_hits in best_by_method.items():
        weighted_hits = tuple(
            (method, hit)
            for method, hit in method_hits.items()
            if _contributes_to_ranking(method, hit.score, semantic_is_available)
        )
        scores[good_type_id] = sum(
            _METHOD_WEIGHTS.get(method, 1.0) * hit.score
            for method, hit in weighted_hits
        )
        if (
            {"FUZZY", "SEMANTIC"}.issubset(method_hits)
            and _contributes_to_ranking(
                "FUZZY", method_hits["FUZZY"].score, semantic_is_available
            )
        ):
            scores[good_type_id] += 0.08 * min(
                method_hits["FUZZY"].score,
                method_hits["SEMANTIC"].score,
            )

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [
        RootCandidate(
            root_good_type_id=root_by_good_type[good_type_id],
            source_good_type_id=good_type_id,
            rank=index + 1,
            score=score,
            methods=tuple(sorted(methods[good_type_id])),
            method_evidence=tuple(
                best_by_method[good_type_id][method]
                for method in sorted(best_by_method[good_type_id])
            ),
            matched_terms=tuple(matched_terms[good_type_id][:3]),
            max_evidence=max_evidence[good_type_id],
            has_ambiguous_term=ambiguous[good_type_id],
        )
        for index, (good_type_id, score) in enumerate(ordered[:top_k])
    ]


def _contributes_to_ranking(
    method: str,
    score: float,
    semantic_is_available: bool,
) -> bool:
    """Keep weak fuzzy matches as recall evidence, never as a semantic vote.

    Approximate matching is deliberately broad so that it can recover spelling
    mistakes.  When semantic retrieval is also available, a low fuzzy score
    often represents a shared generic word (for example, ``bags``).  Such a
    match may remain visible in diagnostics, but must not alter root ranking.
    """
    return not (
        semantic_is_available
        and method == "FUZZY"
        and score < _MIN_FUZZY_SCORE_FOR_SEMANTIC_FUSION
    )
