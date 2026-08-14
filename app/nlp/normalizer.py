from __future__ import annotations

import re
import unicodedata

_ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
_TATWEEL = "\u0640"
_PUNCTUATION = re.compile(r"[^\w\s\u0600-\u06ff]", re.UNICODE)
_WHITESPACE = re.compile(r"\s+")
_REPEATED_VOWELS = re.compile(r"([او])\1+")
_LONG_REPEATED_ARABIC = re.compile(r"([\u0600-\u06ff])\1{2,}")
_LONG_REPEATED_LATIN = re.compile(r"([a-zA-Z])\1{2,}")

_ARABIC_CHAR_MAP = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ؤ": "و",
        "ء": "",
        "ة": "ه",
    }
)


def normalize_text(text: str) -> str:
    value = unicodedata.normalize("NFKC", text or "")
    value = value.replace(_TATWEEL, "")
    value = _ARABIC_DIACRITICS.sub("", value)
    value = value.translate(_ARABIC_CHAR_MAP)
    value = value.casefold()
    value = _REPEATED_VOWELS.sub(r"\1", value)
    value = _LONG_REPEATED_ARABIC.sub(r"\1", value)
    value = _LONG_REPEATED_LATIN.sub(r"\1", value)
    value = _PUNCTUATION.sub(" ", value)
    value = _WHITESPACE.sub(" ", value).strip()
    return value


def compact_text(normalized_text: str) -> str:
    return normalized_text.replace(" ", "")


def normalized_variants(text: str) -> tuple[str, ...]:
    normalized = normalize_text(text)
    if not normalized:
        return ()
    compact = compact_text(normalized)
    if compact and compact != normalized:
        return (normalized, compact)
    return (normalized,)
