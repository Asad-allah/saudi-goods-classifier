from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

Language = Literal["AR", "EN", "MIXED", "OTHER"]
Reason = Literal[
    "EXACT",
    "LEXICAL_VARIANT",
    "HYBRID_STRONG",
    "AMBIGUOUS",
    "LOW_EVIDENCE",
    "UNSUPPORTED_LANGUAGE",
    "MULTI_CATEGORY",
    "EMBEDDING_UNAVAILABLE",
]
SearchMethod = Literal["EXACT", "LEXICAL_VARIANT", "FUZZY", "SEMANTIC"]
FeedbackSource = Literal["DRIVER_SELECTION", "OPERATOR_REVIEW", "DEMO"]
TrainingEligibility = Literal[
    "PENDING_REVIEW",
    "CANDIDATE_AFTER_VALIDATION",
    "NOT_FOR_TRAINING",
]


class ClassifyRequest(BaseModel):
    request_id: str = Field(alias="requestId", min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=191)

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class CategoryResponse(BaseModel):
    id: int
    name_ar: str = Field(alias="nameAr")
    name_en: str = Field(alias="nameEn")
    rank: int
    parent_id: int | None = Field(default=None, alias="parentId")
    root_id: int | None = Field(default=None, alias="rootId")
    is_selectable: bool = Field(default=True, alias="isSelectable")

    model_config = ConfigDict(populate_by_name=True)


class MethodEvidenceResponse(BaseModel):
    method: SearchMethod
    matched_term: str = Field(alias="matchedTerm")
    score: float
    rank: int

    model_config = ConfigDict(populate_by_name=True)


class MatchSignalsResponse(BaseModel):
    """Evidence used for the top direct-good-type decision."""

    methods: list[SearchMethod]
    evidence: list[MethodEvidenceResponse]
    matched_terms: list[str] = Field(alias="matchedTerms")
    max_evidence: float = Field(alias="maxEvidence")
    score_margin: float | None = Field(alias="scoreMargin")

    model_config = ConfigDict(populate_by_name=True)


class ClassifyResponse(BaseModel):
    request_id: str = Field(alias="requestId")
    normalized_text: str = Field(alias="normalizedText")
    catalog_version: str = Field(alias="catalogVersion")
    model_version: str = Field(alias="modelVersion")
    language: Language
    direct_good_type: CategoryResponse | None = Field(alias="directGoodType")
    root_good_type: CategoryResponse | None = Field(alias="rootGoodType")
    alternatives: list[CategoryResponse]
    match_signals: MatchSignalsResponse = Field(alias="matchSignals")
    requires_review: bool = Field(alias="requiresReview")
    reason: Reason
    latency_ms: int = Field(alias="latencyMs")

    model_config = ConfigDict(populate_by_name=True)


class ClassificationFeedbackRequest(BaseModel):
    """A human selection linked to one prior classification request."""

    feedback_id: str = Field(alias="feedbackId", min_length=1, max_length=80)
    selected_good_type_id: int = Field(
        validation_alias=AliasChoices("selectedGoodTypeId", "selectedRootGoodTypeId"),
        serialization_alias="selectedGoodTypeId",
        ge=1,
    )
    source: FeedbackSource

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class ClassificationFeedbackResponse(BaseModel):
    feedback_id: str = Field(alias="feedbackId")
    request_id: str = Field(alias="requestId")
    selected_good_type: CategoryResponse = Field(alias="selectedGoodType")
    training_eligibility: TrainingEligibility = Field(alias="trainingEligibility")

    model_config = ConfigDict(populate_by_name=True)


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorPayload
