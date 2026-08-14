from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from difflib import SequenceMatcher

from app.catalog.models import SearchTerm
from app.nlp.lexical import normalized_tokens, text_token_variants
from app.search.models import CandidateHit

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover - exercised only without dependency
    fuzz = None


_SOFT_SUBSTITUTIONS = {
    # 1. القاف وتباديلها اللهجية (همزة/ألف، كاف، غين، جيم)
    frozenset({"ق", "ا"}),  # قلم <-> الم, قهوة <-> اهوة, قماش <-> اماش
    frozenset({"ق", "ك"}),  # قلم <-> كلم, سكراب <-> سقراب
    frozenset({"ق", "غ"}),  # قصدير <-> غصدير, قرطاس <-> غرطاس
    frozenset({"ق", "ج"}),  # قمر <-> جمر, قريب <-> جريب
    # 2. الجيم والياء الخليجية
    frozenset({"ج", "ي"}),  # دجاج <-> دياي, مسجد <-> ميد
    # 3. الثاء والتاء والسين
    frozenset({"ث", "ت"}),  # ثلاجة <-> تلاجة, ثوم <-> توم, أثاث <-> اتات
    frozenset({"ث", "س"}),  # أثاث <-> اساس, ثوم <-> سوم
    # 4. الذال والدال والزاي
    frozenset({"ذ", "د"}),  # فولاذ <-> فولاد, ذرة <-> درة, ذهب <-> دهب
    frozenset({"ذ", "ز"}),  # أرز <-> ارذ, بذور <-> بزور, ذرة <-> زرة
    # 5. الضاد والظاء والزاي
    frozenset({"ض", "ظ"}),  # منظفات <-> منضفات, حفاضات <-> حفاظات, ظهر <-> ضهر
    frozenset({"ظ", "ز"}),  # نظارة <-> نزارة, عظيم <-> عزيم
    # 6. السين والصاد
    frozenset({"س", "ص"}),  # صابون <-> سابون, صلصة <-> سلصة, سكراب <-> صكراب
    # 7. التاء والطاء
    frozenset({"ت", "ط"}),  # طماطم <-> تماتم, بطاطا <-> بتاتا
    # 8. النهايات اللهجية (التاء/الألف/الياء/الألف المقصورة)
    frozenset({"ه", "ا"}),  # بطاطا <-> بطاطه, كوسا <-> كوسه
    frozenset({"ى", "ي"}),  # مستشفى <-> مستشفي
}


def _arabic_similarity(s1: str, s2: str) -> float:
    """Computes specialized Arabic similarity with soft phonetic, dialectal, and vowel drop weighting."""
    from app.nlp.normalizer import normalize_text

    n1 = normalize_text(s1)
    n2 = normalize_text(s2)
    if n1 == n2:
        return 100.0

    # Interchangeable terminal ه vs ا
    if (n1.endswith("ه") and n2.endswith("ا") and n1[:-1] == n2[:-1]) or (
        n1.endswith("ا") and n2.endswith("ه") and n1[:-1] == n2[:-1]
    ):
        return 98.0

    if fuzz is None:
        return SequenceMatcher(None, n1, n2).ratio() * 100

    ratio = float(fuzz.ratio(n1, n2))
    from rapidfuzz import distance

    lev = distance.Levenshtein.distance(n1, n2)
    max_len = max(len(n1), len(n2))

    if lev <= 2 and max_len >= 3:
        # Vowel drop (ا, و, ي)
        if abs(len(n1) - len(n2)) == 1:
            diff_char = set(n1) ^ set(n2)
            if diff_char & {"ا", "و", "ي"}:
                return max(ratio, 92.0)
        # Soft phonetic and dialect substitutions
        diffs = [frozenset({c1, c2}) for c1, c2 in zip(n1, n2) if c1 != c2]
        if diffs and all(d in _SOFT_SUBSTITUTIONS for d in diffs):
            return max(ratio, 94.0 if len(diffs) == 1 else 90.0)

    return ratio


def _score(
    query: str,
    query_token_variants: frozenset[str],
    term: SearchTerm,
    *,
    specific_variants: frozenset[str],
    idf: dict[str, float] | None = None,
) -> float:
    choices = [term.normalized_term]
    if term.compact_term != term.normalized_term:
        choices.append(term.compact_term)

    best = 0.0
    q_tokens = list(normalized_tokens(query))
    is_single_token = len(q_tokens) == 1

    for choice in choices:
        c_tokens = list(normalized_tokens(choice))
        if not c_tokens:
            continue

        # Single word query vs multi-word term with TF-IDF weighting
        if is_single_token and len(c_tokens) > 1:
            q = q_tokens[0]
            choice_idf_total = sum(idf.get(c, 1.0) for c in c_tokens) if idf else float(len(c_tokens))
            best_token_score = 0.0
            best_c_idf = 1.0
            for c in c_tokens:
                # Reject noise tokens < 3 characters unless exact
                if (len(c) < 3 or len(q) < 3) and c != q:
                    continue
                if not _is_unsafe_fuzzy_distortion(q, c):
                    sim = _arabic_similarity(q, c)
                    if sim > best_token_score:
                        best_token_score = sim
                        best_c_idf = idf.get(c, 1.0) if idf else 1.0

            if best_token_score >= 95.0:
                if len(c_tokens) <= 3:
                    best = max(best, best_token_score)
                else:
                    token_coverage = best_c_idf / max(choice_idf_total, 1.0)
                    best = max(best, best_token_score * (0.5 + 0.5 * token_coverage))
            elif best_token_score >= 80.0:
                token_coverage = best_c_idf / max(choice_idf_total, 1.0)
                best = max(best, best_token_score * (token_coverage ** 0.5))
            continue

        if _is_unsafe_fuzzy_distortion(query, choice):
            continue

        best = max(
            best,
            _arabic_similarity(query, choice),
            float(fuzz.token_set_ratio(query, choice)) if fuzz is not None else 0.0,
        )

    if query_token_variants & text_token_variants(term.normalized_term) & specific_variants:
        term_tokens = set(normalized_tokens(term.normalized_term))
        if len(term_tokens) <= 1 or (len(set(q_tokens) & term_tokens) / len(term_tokens) >= 0.5):
            best = max(best, 98.0)
    return best


def _is_unsafe_fuzzy_distortion(query: str, choice: str) -> bool:
    """Rejects spurious phonetic matches where character edit distance is too large or roots conflict."""
    from app.nlp.normalizer import normalize_text

    q_clean = normalize_text(query.strip())
    c_clean = normalize_text(choice.strip())

    if (len(q_clean) < 3 or len(c_clean) < 3) and q_clean != c_clean:
        return True

    # For single-word query vs single-word choice:
    if " " not in q_clean and " " not in c_clean:
        if len(q_clean) <= 6:
            # Different starting letter on short words without shared prefix
            if q_clean[0] != c_clean[0]:
                return True
            if fuzz is not None:
                from rapidfuzz import distance
                if distance.Levenshtein.distance(q_clean, c_clean) > 1:
                    return True
        elif len(q_clean) <= 9:
            if fuzz is not None:
                from rapidfuzz import distance
                if distance.Levenshtein.distance(q_clean, c_clean) > 2:
                    return True
    return False


def _unsafe_short_token_match(query: str, choice: str) -> bool:
    query_tokens = set(normalized_tokens(query))
    choice_tokens = set(normalized_tokens(choice))
    if not choice_tokens:
        return False
    if choice_tokens & query_tokens:
        return False
    return all(len(token) < 3 for token in choice_tokens)


class FuzzyRetriever:
    def __init__(self, terms: Iterable[SearchTerm], *, min_score: float = 60.0) -> None:
        import math

        self._terms = tuple(terms)
        self._min_score = min_score

        # Precompute Document Frequencies (DF) and IDF for every token in catalog
        doc_freq: dict[str, set[int]] = defaultdict(set)
        for term in self._terms:
            for tok in normalized_tokens(term.normalized_term):
                doc_freq[tok].add(term.source_good_type_id)

        distinct_good_types = len({term.source_good_type_id for term in self._terms}) or 90
        self._idf: dict[str, float] = {
            tok: math.log(1.0 + (distinct_good_types / (len(cat_set) + 1.0))) + 1.0
            for tok, cat_set in doc_freq.items()
        }

        variant_good_types: dict[str, set[int]] = defaultdict(set)
        variant_terms: dict[str, int] = defaultdict(int)
        for term in self._terms:
            for variant in text_token_variants(term.normalized_term):
                variant_good_types[variant].add(term.source_good_type_id)
                variant_terms[variant] += 1
        self._specific_variants = frozenset(
            variant
            for variant, good_types in variant_good_types.items()
            if len(variant) >= 5
            and len(good_types) == 1
            and variant_terms[variant] <= 6
        )

    def search(
        self,
        query: str,
        *,
        top_k: int = 20,
        min_score: float | None = None,
    ) -> list[CandidateHit]:
        scored: list[CandidateHit] = []
        threshold = self._min_score if min_score is None else min_score
        query_token_variants = text_token_variants(query)
        for term in self._terms:
            score = _score(
                query,
                query_token_variants,
                term,
                specific_variants=self._specific_variants,
                idf=self._idf,
            )
            if score < threshold:
                continue
            scored.append(
                CandidateHit(
                    root_good_type_id=term.root_good_type_id,
                    source_good_type_id=term.source_good_type_id,
                    rank=0,
                    score=score / 100,
                    method="FUZZY",
                    matched_term=term.raw_term,
                    is_cross_root_ambiguous=term.is_cross_root_ambiguous,
                    is_cross_good_type_ambiguous=term.is_cross_good_type_ambiguous,
                )
            )

        scored.sort(key=lambda hit: hit.score, reverse=True)
        return [
            CandidateHit(
                root_good_type_id=hit.root_good_type_id,
                source_good_type_id=hit.source_good_type_id,
                rank=index + 1,
                score=hit.score,
                method=hit.method,
                matched_term=hit.matched_term,
                is_cross_root_ambiguous=hit.is_cross_root_ambiguous,
                is_cross_good_type_ambiguous=hit.is_cross_good_type_ambiguous,
            )
            for index, hit in enumerate(scored[:top_k])
        ]
