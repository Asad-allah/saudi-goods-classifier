from __future__ import annotations

import re
import unicodedata

from rapidfuzz import process
from rapidfuzz.distance import Levenshtein
from wordfreq import zipf_frequency

from app.catalog.models import Catalog
from app.nlp.lexical import normalized_tokens, token_variants
from app.nlp.normalizer import compact_text, normalize_text

_TOKEN_PATTERN = re.compile(r"[a-z]+|[\u0621-\u064a]+")
_LATIN_KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
_ARABIC_KEYBOARD_ROWS = ("ضصثقفغعهخحجد", "شسيبلاتنمكط", "ئءورلايهوزظ")
_VOWELS = frozenset("aeiouy")
_IGNORED_CONNECTORS = frozenset({"و"})
_MIN_ZIPF_FREQUENCY = 2.5


class InputRejected(ValueError):
    """Base error for input that must never reach retrieval."""

    code = "INPUT_NOT_MEANINGFUL"
    validation_reason = "UNSPECIFIED"

    def __init__(self, validation_reason: str | None = None) -> None:
        self.validation_reason = validation_reason or type(self).validation_reason
        super().__init__(self.validation_reason)


class InputNotMeaningful(InputRejected):
    """Raised when the text cannot safely be treated as a goods description."""

    message = (
        "أدخل وصفاً مفهوماً للبضاعة من 3 أحرف على الأقل؛ "
        "لا تُدخل أرقاماً فقط أو حروفاً مكررة أو عشوائية."
    )


class InputNeedsContext(InputRejected):
    """Raised when a word-shaped unknown label cannot identify a goods type."""

    code = "INSUFFICIENT_CONTEXT"
    validation_reason = "INSUFFICIENT_CONTEXT"
    message = (
        "اكتب نوع البضاعة مع العلامة أو الموديل، مثلاً: "
        "حليب نيدو أو تلفزيون سامسونج."
    )


class InputQualityGate:
    """Reject obvious noise before it reaches fuzzy or semantic classification."""

    def __init__(self, catalog: Catalog) -> None:
        self._known_terms = {
            variant
            for term in catalog.terms
            for variant in (term.normalized_term, term.compact_term)
            if variant
        }
        self._known_token_variants = frozenset(
            variant
            for term in catalog.terms
            for token in normalized_tokens(term.normalized_term)
            if token not in _IGNORED_CONNECTORS
            for variant in token_variants(token)
        )
        self._arabic_trigrams = {
            trigram
            for term in catalog.terms
            for token in _arabic_tokens(term.normalized_term)
            for trigram in _trigrams(token)
        }

    def require_meaningful(self, text: str) -> None:
        normalized = normalize_text(text)
        compact = compact_text(normalized)
        tokens = normalized_tokens(normalized)
        lexical_tokens = _lexical_tokens(text)

        if not _contains_any_letter(normalized):
            raise InputNotMeaningful("NO_LETTERS")
        if not tokens:
            # Keep non-Arabic/non-English text on the existing review path.
            return
        token_pairs = tuple(zip(tokens, lexical_tokens, strict=False))
        content_pairs = tuple(
            pair for pair in token_pairs if pair[0] not in _IGNORED_CONNECTORS
        )
        if not content_pairs:
            raise InputNotMeaningful("NO_CONTENT_WORD")
        # Judge the description as a whole. A noisy token must not reject a
        # phrase when another content word is usable (for example, "باب خشب").
        usable_pairs: list[tuple[str, str]] = []
        rejected_reasons: list[str] = []
        for normalized_token, lexical_token in content_pairs:
            reason = self._token_rejection_reason(normalized_token, lexical_token)
            if reason is None:
                usable_pairs.append((normalized_token, lexical_token))
            else:
                rejected_reasons.append(reason)
        if not usable_pairs:
            raise InputNotMeaningful(_aggregate_rejection_reason(rejected_reasons))
        if normalized in self._known_terms or compact in self._known_terms:
            return
        # Retrieval is allowed only after a catalog or language anchor. This
        # prevents a random token from becoming a category through embedding
        # similarity while keeping unknown brands beside a real item usable.
        if not any(
            self._has_catalog_token_anchor(normalized_token)
            or _has_lexical_evidence(normalized_token, lexical_token)
            for normalized_token, lexical_token in usable_pairs
        ):
            if all(
                self._is_structurally_plausible(normalized_token)
                for normalized_token, _ in usable_pairs
            ):
                raise InputNeedsContext
            raise InputNotMeaningful("NO_LEXICAL_EVIDENCE")

    def _token_rejection_reason(
        self,
        normalized_token: str,
        lexical_token: str,
    ) -> str | None:
        if (
            _is_repeated_noise(normalized_token)
            or _is_repeated_noise(lexical_token)
        ) and not self._has_catalog_token_anchor(normalized_token):
            return "REPEATED_NOISE"
        if len(normalized_token) < 3 and not self._has_catalog_token_anchor(
            normalized_token
        ):
            return "TOKEN_TOO_SHORT"
        if _is_keyboard_mash(normalized_token) and not (
            self._has_catalog_token_anchor(normalized_token)
            or _has_lexical_evidence(normalized_token, lexical_token)
        ):
            return "KEYBOARD_MASH"
        return None

    def _has_catalog_token_anchor(self, token: str) -> bool:
        variants = token_variants(token)
        if variants & self._known_token_variants:
            return True

        # Allow a small typo only after comparing the incoming token and the
        # catalog token through the exact same normalized representation.
        # This is deliberately stricter than the later retrieval threshold.
        for variant in variants:
            match = process.extractOne(
                variant,
                self._known_token_variants,
                scorer=Levenshtein.normalized_similarity,
                score_cutoff=0.84,
                score_hint=0.9,
            )
            if match is None:
                continue
            candidate = match[0]
            distance = Levenshtein.distance(variant, candidate)
            if distance <= _max_typo_distance(variant, candidate):
                return True
        return False

    def _is_structurally_plausible(self, token: str) -> bool:
        if not _is_arabic_token(token):
            return _is_latin_word_like(token)
        trigrams = _trigrams(token)
        if not trigrams:
            return False
        coverage = sum(item in self._arabic_trigrams for item in trigrams) / len(trigrams)
        return coverage >= 0.5


def _contains_any_letter(text: str) -> bool:
    return any(unicodedata.category(char).startswith("L") for char in text)


def _arabic_tokens(text: str) -> tuple[str, ...]:
    return tuple(token for token in normalized_tokens(text) if _is_arabic_token(token))


def _lexical_tokens(text: str) -> tuple[str, ...]:
    """Keep spelling needed by wordfreq; classifier normalization is lossy."""
    value = unicodedata.normalize("NFKC", text or "")
    value = "".join(
        char
        for char in value
        if char != "ـ" and not unicodedata.category(char).startswith("M")
    )
    return tuple(_TOKEN_PATTERN.findall(value.casefold()))


def _is_arabic_token(token: str) -> bool:
    return bool(token) and all("\u0621" <= char <= "\u064a" for char in token)


def _trigrams(token: str) -> tuple[str, ...]:
    bounded = f"^{token}$"
    return tuple(bounded[index : index + 3] for index in range(len(bounded) - 2))


def _is_repeated_noise(token: str) -> bool:
    if len(token) < 3:
        return False
    highest_count = max(token.count(char) for char in set(token))
    # A run such as "سسسسح" is noise even though it has two distinct letters.
    # The ratio catches dispersed repetition such as "زززجزز" as well.
    has_long_run = bool(re.search(r"(.)\1{2,}", token))
    has_dominant_character = len(token) >= 5 and highest_count / len(token) >= 0.6
    return has_long_run or has_dominant_character


def _aggregate_rejection_reason(reasons: list[str]) -> str:
    unique_reasons = set(reasons)
    if len(unique_reasons) == 1:
        return reasons[0]
    return "NO_VALID_CONTENT_WORD"


def _is_keyboard_mash(token: str) -> bool:
    rows = _ARABIC_KEYBOARD_ROWS if _is_arabic_token(token) else _LATIN_KEYBOARD_ROWS
    lowered = token.casefold()
    return any(
        lowered[index : index + 3] in row or lowered[index : index + 3] in row[::-1]
        for row in rows
        for index in range(len(lowered) - 2)
    )


def _is_latin_word_like(token: str) -> bool:
    vowels = sum(char in _VOWELS for char in token)
    if not vowels:
        return False
    return not re.search(r"[^aeiouy]{4,}", token)


def _has_lexical_evidence(normalized_token: str, lexical_token: str) -> bool:
    language = "ar" if _is_arabic_token(normalized_token) else "en"
    variants = {lexical_token, normalized_token}
    if language == "ar" and lexical_token.endswith("ه"):
        variants.add(f"{lexical_token[:-1]}ة")
    return max(zipf_frequency(variant, language) for variant in variants) >= _MIN_ZIPF_FREQUENCY


def _max_typo_distance(left: str, right: str) -> int:
    shortest = min(len(left), len(right))
    if shortest < 5:
        return 0
    if shortest < 9:
        return 1
    return 2
