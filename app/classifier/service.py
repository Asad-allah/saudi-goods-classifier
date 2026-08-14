from __future__ import annotations

import re
import time
from collections import defaultdict

from app.catalog.models import Catalog, SearchTerm
from app.classifier.models import ClassificationResult
from app.classifier.policy import decide
from app.nlp.input_quality import InputQualityGate
from app.nlp.language import detect_language
from app.nlp.lexical import normalized_tokens, text_token_variants, token_variants
from app.nlp.normalizer import compact_text, normalize_text
from app.search.fusion import fuse_hits
from app.search.fuzzy import FuzzyRetriever
from app.search.models import CandidateHit
from app.search.semantic import BaseSemanticRetriever


class CatalogNotReady(RuntimeError):
    pass


_CONTAINER_TOKENS = {
    "كيس", "اكياس", "أكياس", "كياس", "خيشة", "خياش", "شوال", "شوالات",
    "كرتون", "كرتونة", "كراتين", "طبلية", "طبالي", "برميل", "براميل",
    "جالون", "جوالين", "علبة", "علب", "شاحنة", "تريلا", "دينا", "سطحة",
    "وايت", "حمولة", "شحنة", "بضاعة", "اغراض", "أغراض", "حبة", "حبات",
    "ربطة", "ربطات", "درزن", "درازن", "كونتينر", "حاوية", "حاويات",
}


class RootCategoryClassifier:
    def __init__(
        self,
        catalog: Catalog,
        *,
        semantic_retriever: BaseSemanticRetriever | None = None,
        input_validation_enabled: bool = True,
    ) -> None:
        if not catalog.roots or not catalog.terms:
            raise CatalogNotReady("Catalog has no roots or search terms")
        self.catalog = catalog
        self._semantic = semantic_retriever or BaseSemanticRetriever()
        self._fuzzy = FuzzyRetriever(catalog.selectable_terms)
        self._exact_lookup = _build_exact_lookup(catalog.selectable_terms)
        self._token_lookup = _build_token_lookup(catalog.selectable_terms)
        self._quality_gate = (
            InputQualityGate(catalog) if input_validation_enabled else None
        )

    @property
    def model_version(self) -> str:
        return self._semantic.model_version

    def classify(self, *, request_id: str, text: str) -> ClassificationResult:
        started = time.perf_counter()
        if self._quality_gate is not None:
            self._quality_gate.require_meaningful(text)
        normalized = normalize_text(text)
        compact = compact_text(normalized)
        language = detect_language(text)

        exact_hits = self._exact_hits(normalized, compact)
        is_full_exact = any(h.method == "EXACT" and not h.is_cross_good_type_ambiguous for h in exact_hits)
        
        fuzzy_hits = []
        semantic_hits = []
        semantic_available = self._semantic.is_available()

        if not is_full_exact:
            if semantic_available:
                semantic_hits = self._semantic.search(normalized, top_k=20)
            if not exact_hits:
                fuzzy_hits = self._fuzzy.search(normalized, top_k=20)

        candidates = fuse_hits(exact_hits + fuzzy_hits + semantic_hits, top_k=5)

        requires_review, reason = decide(
            candidates,
            language=language,
            embedding_available=semantic_available,
        )
        multi_category_reason = self._detect_multi_category(text)
        if multi_category_reason:
            requires_review = True
            reason = multi_category_reason
        top_category = (
            None
            if _should_abstain(candidates, requires_review=requires_review, reason=reason)
            else candidates[0]
        )

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return ClassificationResult(
            request_id=request_id,
            normalized_text=normalized,
            catalog_version=self.catalog.version,
            model_version=self.model_version,
            language=language,
            top_category=top_category,
            alternatives=tuple(candidates),
            requires_review=requires_review,
            reason=reason,
            latency_ms=elapsed_ms,
        )

    def _exact_hits(self, normalized: str, compact: str) -> list[CandidateHit]:
        phrase_keys = [normalized]
        if compact != normalized:
            phrase_keys.append(compact)
        hits: list[CandidateHit] = []
        seen_good_types: set[int] = set()

        for key in phrase_keys:
            self._append_term_hits(
                hits,
                self._exact_lookup.get(key, ()),
                seen_good_types,
                method="EXACT",
                score=1.0,
            )

        if hits:
            return _mark_collection_ambiguity(hits)

        # For short queries (<= 2 tokens), check non-container token variants (e.g. بسكوتة -> بسكوت)
        tokens = list(normalized_tokens(normalized))
        if len(tokens) <= 2:
            for token in tokens:
                if len(tokens) > 1 and token in _CONTAINER_TOKENS:
                    continue
                for variant in token_variants(token):
                    self._append_term_hits(
                        hits,
                        self._token_lookup.get(variant, ()),
                        seen_good_types,
                        method="LEXICAL_VARIANT",
                        score=0.99,
                    )
        return _mark_collection_ambiguity(hits)

    def _append_term_hits(
        self,
        hits: list[CandidateHit],
        terms: tuple[SearchTerm, ...],
        seen_good_types: set[int],
        *,
        method: str,
        score: float,
    ) -> None:
        is_collection_ambiguous = len({term.source_good_type_id for term in terms}) > 1
        for term in terms:
            if term.source_good_type_id in seen_good_types:
                continue
            seen_good_types.add(term.source_good_type_id)
            hits.append(
                CandidateHit(
                    root_good_type_id=term.root_good_type_id,
                    source_good_type_id=term.source_good_type_id,
                    rank=len(hits) + 1,
                    score=score,
                    method=method,
                    matched_term=term.raw_term,
                    is_cross_root_ambiguous=(
                        term.is_cross_root_ambiguous or is_collection_ambiguous
                    ),
                    is_cross_good_type_ambiguous=(
                        term.is_cross_good_type_ambiguous or is_collection_ambiguous
                    ),
                )
            )

    def _detect_multi_category(self, raw_text: str) -> str | None:
        parts = [
            normalize_text(part)
            for part in re.split(r"\s*(?:\+|/|،|,|\sو\s)\s*", raw_text)
            if normalize_text(part)
        ]
        if len(parts) < 2:
            return None

        roots: set[int] = set()
        for part in parts:
            roots.update(self._candidate_roots_for_exact_part(part))
        if len(roots) > 1:
            return "MULTI_CATEGORY"
        return None

    def _candidate_roots_for_exact_part(self, normalized_part: str) -> set[int]:
        compact = compact_text(normalized_part)
        return {
            hit.root_good_type_id
            for hit in self._exact_hits(normalized_part, compact)
            if hit.method in {"EXACT", "LEXICAL_VARIANT"}
        }


def _should_abstain(
    candidates: list,
    *,
    requires_review: bool,
    reason: str,
) -> bool:
    if not candidates:
        return True
    if not requires_review:
        return False
    return reason in {
        "AMBIGUOUS",
        "LOW_EVIDENCE",
        "UNSUPPORTED_LANGUAGE",
        "MULTI_CATEGORY",
        "EMBEDDING_UNAVAILABLE",
    }


def _mark_collection_ambiguity(hits: list[CandidateHit]) -> list[CandidateHit]:
    if len({hit.source_good_type_id for hit in hits}) <= 1:
        return hits
    return [
        CandidateHit(
            root_good_type_id=hit.root_good_type_id,
            source_good_type_id=hit.source_good_type_id,
            rank=hit.rank,
            score=hit.score,
            method=hit.method,
            matched_term=hit.matched_term,
            is_cross_root_ambiguous=True,
            is_cross_good_type_ambiguous=True,
        )
        for hit in hits
    ]


def _build_exact_lookup(terms: tuple[SearchTerm, ...]) -> dict[str, tuple[SearchTerm, ...]]:
    lookup: dict[str, list[SearchTerm]] = defaultdict(list)
    for term in terms:
        lookup[term.normalized_term].append(term)
        if term.compact_term != term.normalized_term:
            lookup[term.compact_term].append(term)
    return {key: tuple(value) for key, value in lookup.items()}


def _build_token_lookup(terms: tuple[SearchTerm, ...]) -> dict[str, tuple[SearchTerm, ...]]:
    variants_to_terms: dict[str, list[SearchTerm]] = defaultdict(list)
    variants_to_good_types: dict[str, set[int]] = defaultdict(set)
    for term in terms:
        # ONLY single-token terms are eligible for standalone token morphological variant matching
        term_tokens = list(normalized_tokens(term.normalized_term))
        if len(term_tokens) == 1:
            for variant in text_token_variants(term.normalized_term):
                variants_to_terms[variant].append(term)
                variants_to_good_types[variant].add(term.source_good_type_id)

    lookup: dict[str, tuple[SearchTerm, ...]] = {}
    for variant, variant_terms in variants_to_terms.items():
        good_type_count = len(variants_to_good_types[variant])
        if len(variant) < 3:
            continue
        if good_type_count > 3 or len(variant_terms) > 8:
            continue
        lookup[variant] = tuple(variant_terms)
    return lookup
