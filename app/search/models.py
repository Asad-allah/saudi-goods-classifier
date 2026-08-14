from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateHit:
    root_good_type_id: int
    source_good_type_id: int
    rank: int
    score: float
    method: str
    matched_term: str
    is_cross_root_ambiguous: bool = False
    is_cross_good_type_ambiguous: bool = False
