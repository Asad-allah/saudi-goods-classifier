from __future__ import annotations

from dataclasses import dataclass

from app.search.fusion import RootCandidate


@dataclass(frozen=True)
class ClassificationResult:
    request_id: str
    normalized_text: str
    catalog_version: str
    model_version: str
    language: str
    top_category: RootCandidate | None
    alternatives: tuple[RootCandidate, ...]
    requires_review: bool
    reason: str
    latency_ms: int
