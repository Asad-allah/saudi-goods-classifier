"""Sanitizer and quality control gate for dataset samples."""

from __future__ import annotations
import re
from app.nlp.normalizer import normalize_text, compact_text
from app.nlp.language import detect_language


_CLEAN_PATTERN = re.compile(r"[^\w\s\-\+\.,/\\#%ء-ي]")


class DatasetSanitizer:
    """Sanitizes text and filters out noise or non-conforming entries."""

    def __init__(self) -> None:
        pass

    def clean(self, text: str) -> str:
        """Cleans and standardizes raw text."""
        # Replace multiple spaces/tabs
        cleaned = re.sub(r"\s+", " ", text).strip()
        # Remove weird non-printable or symbol noise
        cleaned = _CLEAN_PATTERN.sub("", cleaned)
        return cleaned.strip()

    def is_acceptable(self, text: str) -> bool:
        """Validates if text passes strict quality requirements."""
        cleaned = self.clean(text)
        if len(cleaned) < 4:
            return False

        normalized = normalize_text(cleaned)
        if len(normalized) < 3:
            return False

        # Must not be digits only
        if normalized.replace(" ", "").isdigit():
            return False

        lang = detect_language(cleaned)
        if lang not in ("AR", "EN", "MIXED"):
            return False

        return True
