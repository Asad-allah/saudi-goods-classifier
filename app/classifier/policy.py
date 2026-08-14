from __future__ import annotations

from app.search.fusion import RootCandidate


def decide(
    candidates: list[RootCandidate],
    *,
    language: str,
    embedding_available: bool,
) -> tuple[bool, str]:
    if language == "OTHER":
        return True, "UNSUPPORTED_LANGUAGE"
    if not candidates:
        return True, "LOW_EVIDENCE"

    top = candidates[0]
    second = candidates[1] if len(candidates) > 1 else None

    if "EXACT" in top.methods:
        if not top.has_ambiguous_term or (second is not None and top.root_good_type_id == second.root_good_type_id):
            return False, "EXACT"
        if top.max_evidence >= 0.99 and (second is None or top.root_good_type_id == second.root_good_type_id):
            return False, "EXACT"
        if second is None:
            return False, "EXACT"

    if top.has_ambiguous_term:
        return True, "AMBIGUOUS"

    if "LEXICAL_VARIANT" in top.methods:
        if second is None or top.score - second.score >= 0.02:
            return False, "LEXICAL_VARIANT"
        return True, "AMBIGUOUS"

    if not embedding_available and "SEMANTIC" not in top.methods:
        return True, "EMBEDDING_UNAVAILABLE"

    method_set = set(top.methods)
    score_margin = top.score - (second.score if second else 0.0)
    evidence_by_method = {
        evidence.method: evidence.score for evidence in top.method_evidence
    }
    if (
        {"FUZZY", "SEMANTIC"}.issubset(method_set)
        and evidence_by_method.get("FUZZY", 0.0) >= 0.86
        and evidence_by_method.get("SEMANTIC", 0.0) >= 0.86
        and (second is None or score_margin >= 0.02)
    ):
        return False, "HYBRID_STRONG"
    if second is not None and score_margin < 0.02:
        return True, "AMBIGUOUS"
    return True, "LOW_EVIDENCE"
