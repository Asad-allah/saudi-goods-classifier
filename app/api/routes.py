from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.api.schemas import (
    CategoryResponse,
    ClassificationFeedbackRequest,
    ClassificationFeedbackResponse,
    ClassifyRequest,
    ClassifyResponse,
    MatchSignalsResponse,
    MethodEvidenceResponse,
)
from app.classifier.events import FeedbackIdConflict, JsonlEventLogger
from app.classifier.models import ClassificationResult
from app.classifier.service import CatalogNotReady, RootCategoryClassifier
from app.core.config import Settings
from app.core.security import require_api_key
from app.nlp.input_quality import InputRejected

router = APIRouter()


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _classifier(request: Request) -> RootCategoryClassifier:
    classifier = getattr(request.app.state, "classifier", None)
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "CATALOG_NOT_READY",
                    "message": "No active catalog/index is ready",
                    "details": {},
                }
            },
        )
    return classifier


def _event_logger(request: Request) -> JsonlEventLogger:
    return request.app.state.event_logger


def _to_response(
    result: ClassificationResult,
    classifier: RootCategoryClassifier,
) -> ClassifyResponse:
    def good_type_response(candidate) -> CategoryResponse:
        good_type = classifier.catalog.good_type(candidate.good_type_id)
        root_id = classifier.catalog.root_id_for(good_type.id)
        return CategoryResponse(
            id=good_type.id,
            name_ar=good_type.name_ar,
            name_en=good_type.name_en,
            rank=candidate.rank,
            parent_id=good_type.parent_id,
            root_id=root_id,
            is_selectable=good_type.is_selectable,
        )

    def root_response(candidate) -> CategoryResponse:
        root = classifier.catalog.root(candidate.root_good_type_id)
        return CategoryResponse(
            id=root.id,
            name_ar=root.name_ar,
            name_en=root.name_en,
            rank=1,
            parent_id=None,
            root_id=root.id,
            is_selectable=classifier.catalog.is_selectable(root.id),
        )

    signal_candidate = result.top_category or (
        result.alternatives[0] if result.alternatives else None
    )
    second_candidate = result.alternatives[1] if len(result.alternatives) > 1 else None
    score_margin = (
        round(signal_candidate.score - second_candidate.score, 4)
        if signal_candidate is not None and second_candidate is not None
        else None
    )
    return ClassifyResponse(
        request_id=result.request_id,
        normalized_text=result.normalized_text,
        catalog_version=result.catalog_version,
        model_version=result.model_version,
        language=result.language,
        direct_good_type=(
            good_type_response(result.top_category)
            if result.top_category is not None
            else None
        ),
        root_good_type=(
            root_response(result.top_category)
            if result.top_category is not None
            else None
        ),
        alternatives=[good_type_response(candidate) for candidate in result.alternatives],
        match_signals=MatchSignalsResponse(
            methods=list(signal_candidate.methods) if signal_candidate else [],
            evidence=[
                MethodEvidenceResponse(
                    method=evidence.method,
                    matched_term=evidence.matched_term,
                    score=round(evidence.score, 4),
                    rank=evidence.rank,
                )
                for evidence in (signal_candidate.method_evidence if signal_candidate else ())
            ],
            matched_terms=list(signal_candidate.matched_terms) if signal_candidate else [],
            max_evidence=round(signal_candidate.max_evidence, 4)
            if signal_candidate
            else 0.0,
            score_margin=score_margin,
        ),
        requires_review=result.requires_review,
        reason=result.reason,
        latency_ms=result.latency_ms,
    )


def _feedback_training_eligibility(source: str) -> str:
    """Keep a user click separate from a label admitted to model training."""
    if source == "OPERATOR_REVIEW":
        return "CANDIDATE_AFTER_VALIDATION"
    if source == "DRIVER_SELECTION":
        return "PENDING_REVIEW"
    return "NOT_FOR_TRAINING"


def _good_type_response(
    classifier: RootCategoryClassifier,
    good_type_id: int,
) -> CategoryResponse:
    try:
        good_type = classifier.catalog.good_type(good_type_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error": {
                    "code": "GOOD_TYPE_UNKNOWN",
                    "message": "selectedGoodTypeId must identify an existing good_type",
                    "details": {},
                }
            },
        ) from exc
    if not good_type.is_selectable:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error": {
                    "code": "GOOD_TYPE_NOT_SELECTABLE",
                    "message": "selectedGoodTypeId must identify a selectable leaf good_type",
                    "details": {},
                }
            },
        )
    root_id = classifier.catalog.root_id_for(good_type.id)
    return CategoryResponse(
        id=good_type.id,
        name_ar=good_type.name_ar,
        name_en=good_type.name_en,
        rank=1,
        parent_id=good_type.parent_id,
        root_id=root_id,
        is_selectable=True,
    )


@router.get("/health")
def health(request: Request) -> dict[str, object]:
    classifier = getattr(request.app.state, "classifier", None)
    if classifier is None:
        return {"status": "not_ready"}
    return {
        "status": "ok",
        "catalogVersion": classifier.catalog.version,
        "rootCount": classifier.catalog.root_count,
        "goodTypeCount": classifier.catalog.good_type_count,
        "selectableGoodTypeCount": classifier.catalog.selectable_count,
        "termCount": classifier.catalog.term_count,
        "modelVersion": classifier.model_version,
    }


@router.post("/v1/classify", response_model=ClassifyResponse, response_model_by_alias=True)
def classify(
    payload: ClassifyRequest,
    request: Request,
    settings: Settings = Depends(_settings),
    classifier: RootCategoryClassifier = Depends(_classifier),
    event_logger: JsonlEventLogger = Depends(_event_logger),
) -> ClassifyResponse:
    require_api_key(request, settings)
    return _classify_without_auth(payload, classifier, event_logger)


@router.post(
    "/v1/classifications/{request_id}/feedback",
    response_model=ClassificationFeedbackResponse,
    response_model_by_alias=True,
)
def classify_feedback(
    request_id: str,
    payload: ClassificationFeedbackRequest,
    request: Request,
    settings: Settings = Depends(_settings),
    classifier: RootCategoryClassifier = Depends(_classifier),
    event_logger: JsonlEventLogger = Depends(_event_logger),
) -> ClassificationFeedbackResponse:
    """Record a human root-category selection for offline learning and audit."""
    require_api_key(request, settings)
    return _record_feedback(request_id, payload, classifier, event_logger)


@router.post("/demo/classify", response_model=ClassifyResponse, response_model_by_alias=True)
def demo_classify(
    payload: ClassifyRequest,
    settings: Settings = Depends(_settings),
    classifier: RootCategoryClassifier = Depends(_classifier),
    event_logger: JsonlEventLogger = Depends(_event_logger),
) -> ClassifyResponse:
    if not settings.demo_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo disabled")
    return _classify_without_auth(payload, classifier, event_logger)


@router.post(
    "/demo/classifications/{request_id}/feedback",
    response_model=ClassificationFeedbackResponse,
    response_model_by_alias=True,
)
def demo_classify_feedback(
    request_id: str,
    payload: ClassificationFeedbackRequest,
    settings: Settings = Depends(_settings),
    classifier: RootCategoryClassifier = Depends(_classifier),
    event_logger: JsonlEventLogger = Depends(_event_logger),
) -> ClassificationFeedbackResponse:
    """Allow the local demo to prove the feedback contract without API credentials."""
    if not settings.demo_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo disabled")
    if payload.source != "DEMO":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error": {
                    "code": "DEMO_SOURCE_REQUIRED",
                    "message": "Demo feedback must use source DEMO",
                    "details": {},
                }
            },
        )
    return _record_feedback(request_id, payload, classifier, event_logger)


@router.post("/semantic/search")
def semantic_search_endpoint(
    payload: dict,
    classifier: RootCategoryClassifier = Depends(_classifier),
) -> dict:
    """Microservice endpoint used by Colab to return semantic FAISS candidate hits."""
    query = str(payload.get("query", ""))
    top_k = int(payload.get("top_k", 20))
    hits = classifier._semantic.search(query, top_k=top_k)
    return {
        "hits": [
            {
                "root_good_type_id": h.root_good_type_id,
                "source_good_type_id": h.source_good_type_id,
                "rank": h.rank,
                "score": round(float(h.score), 4),
                "matched_term": h.matched_term,
                "is_cross_root_ambiguous": h.is_cross_root_ambiguous,
                "is_cross_good_type_ambiguous": h.is_cross_good_type_ambiguous,
            }
            for h in hits
        ]
    }


@router.post("/demo/configure-semantic")
def configure_remote_semantic(
    payload: dict,
    request: Request,
    classifier: RootCategoryClassifier = Depends(_classifier),
) -> dict:
    """Dynamically connect Render to Google Colab GPU Semantic AI Engine."""
    remote_url = str(payload.get("url", "")).strip()
    if remote_url:
        classifier.set_semantic_retriever(RemoteSemanticRetriever(remote_url))
    else:
        classifier.set_semantic_retriever(BaseSemanticRetriever())
    return {
        "status": "ok",
        "remote_url": remote_url,
        "is_available": classifier._semantic.is_available(),
    }


def _classify_without_auth(
    payload: ClassifyRequest,
    classifier: RootCategoryClassifier,
    event_logger: JsonlEventLogger,
) -> ClassifyResponse:
    try:
        result = classifier.classify(request_id=payload.request_id, text=payload.text)
    except InputRejected as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": {"validationReason": exc.validation_reason},
                }
            },
        ) from exc
    except CatalogNotReady as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "CATALOG_NOT_READY",
                    "message": str(exc),
                    "details": {},
                }
            },
        ) from exc

    response = _to_response(result, classifier)
    event_logger.write(
        {
            **response.model_dump(by_alias=True),
            "eventType": "CLASSIFICATION",
            "recordedAt": datetime.now(UTC).isoformat(),
            "text": payload.text,
            "normalizedText": result.normalized_text,
        }
    )
    return response


def _record_feedback(
    request_id: str,
    payload: ClassificationFeedbackRequest,
    classifier: RootCategoryClassifier,
    event_logger: JsonlEventLogger,
) -> ClassificationFeedbackResponse:
    good_type = _good_type_response(classifier, payload.selected_good_type_id)
    if not event_logger.has_classification(request_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "CLASSIFICATION_REQUEST_UNKNOWN",
                    "message": "requestId does not identify a recorded classification",
                    "details": {},
                }
            },
        )
    training_eligibility = _feedback_training_eligibility(payload.source)
    event = {
        "eventType": "CLASSIFICATION_FEEDBACK",
        "recordedAt": datetime.now(UTC).isoformat(),
        "feedbackId": payload.feedback_id,
        "requestId": request_id,
        "selectedGoodTypeId": payload.selected_good_type_id,
        "selectedRootGoodTypeId": good_type.root_id,
        "source": payload.source,
        "trainingEligibility": training_eligibility,
        "catalogVersion": classifier.catalog.version,
        "modelVersion": classifier.model_version,
    }
    try:
        event_logger.write_feedback_once(event)
    except FeedbackIdConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "FEEDBACK_ID_CONFLICT",
                    "message": "feedbackId was already used for a different correction",
                    "details": {},
                }
            },
        ) from exc
    return ClassificationFeedbackResponse(
        feedback_id=payload.feedback_id,
        request_id=request_id,
        selected_good_type=good_type,
        training_eligibility=training_eligibility,
    )


def _render_v19_html() -> str:
    trace_path = Path(".superpowers/brainstorm/37-1786645466/content/engineering-live-trace-v19-local-api.html")
    if trace_path.exists():
        content = trace_path.read_text(encoding="utf-8")
        # Ensure API url uses relative endpoint for 100% reliable local fetching
        content = content.replace('const apiUrl = "http://127.0.0.1:8000/demo/classify";', 'const apiUrl = "/demo/classify";')
        contract_meta = """
<!-- مسار القرار والهندسة المباشرة -->
<script id="api-contract-metadata" type="application/json">
{
  "decisionPath": "مسار القرار",
  "matchSignals": true,
  "endpoints": ["/demo/classify", "/demo/classifications/"],
  "actions": ["submitFeedback", "invalidateResult", "preflightInputError"]
}
</script>
"""
        return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dandan | V19 Engineering Live Trace Dashboard</title>
</head>
<body style="margin:0;background:#f1f4f1;">
{contract_meta}
{content}
</body>
</html>"""
    return _DEMO_HTML


@router.get("/", response_class=HTMLResponse)
@router.get("/v19", response_class=HTMLResponse)
@router.get("/trace", response_class=HTMLResponse)
@router.get("/engineering", response_class=HTMLResponse)
def v19_engineering_page(settings: Settings = Depends(_settings)) -> HTMLResponse:
    if not settings.demo_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo disabled")
    return HTMLResponse(_render_v19_html())


@router.get("/classic", response_class=HTMLResponse)
def classic_demo_page(settings: Settings = Depends(_settings)) -> HTMLResponse:
    if not settings.demo_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo disabled")
    return HTMLResponse(_DEMO_HTML)


_DEMO_HTML = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0d2732">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%230d2732'/%3E%3Cpath d='M16 33h32M39 22l10 11-10 11' stroke='%235ee0ad' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
  <title>دندن | مختبر تصنيف البضائع</title>
  <style>
    :root { --ink: #102833; --muted: #5c6d75; --surface: #fffef9; --canvas: #edf2ef; --line: #d9e2de; --accent: #087f5b; --accent-deep: #056449; --mint: #e1f6ed; --blue: #e8f2fb; --amber: #fff3db; --danger: #fff0ec; --radius: 14px; }
    * { box-sizing: border-box; }
    body { margin: 0; min-width: 320px; background: var(--canvas); color: var(--ink); font-family: Tahoma, "Segoe UI", Arial, sans-serif; line-height: 1.6; }
    button, textarea { font: inherit; }
    button { touch-action: manipulation; }
    .shell { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 48px; }
    .topbar { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; padding: 0 0 24px; border-bottom: 1px solid var(--line); }
    .brand { display: flex; align-items: center; gap: 12px; }
    .brand-mark { display: grid; place-items: center; width: 42px; height: 42px; border-radius: 12px; background: var(--ink); color: #5ee0ad; font-size: 24px; font-weight: 700; }
    .eyebrow { margin: 0 0 2px; color: var(--muted); font-size: .82rem; font-weight: 700; }
    .brand h1 { margin: 0; font-size: clamp(1.35rem, 2.6vw, 1.85rem); line-height: 1.2; }
    .service-state { display: inline-flex; align-items: center; gap: 8px; margin-top: 4px; padding: 7px 10px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); background: #fff; font-size: .84rem; white-space: nowrap; }
    .service-state::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: #8fa49c; }
    .service-state.ready::before { background: #0f9d6d; box-shadow: 0 0 0 4px #dff5ec; }
    .service-state.warning::before { background: #c58109; box-shadow: 0 0 0 4px #fff1d7; }
    .service-state.error::before { background: #cf4b32; }
    .intro { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 24px; align-items: end; padding: 30px 0; }
    .intro h2 { max-width: 760px; margin: 0; font-size: clamp(1.65rem, 3.8vw, 2.55rem); line-height: 1.3; letter-spacing: -.02em; }
    .intro p { max-width: 620px; margin: 10px 0 0; color: var(--muted); }
    .catalog-stat { align-self: center; padding: 12px 16px; border-right: 3px solid var(--accent); color: var(--muted); background: #f8fbf9; font-size: .86rem; }
    .catalog-stat strong { display: block; color: var(--ink); font-size: 1.2rem; }
    .workspace { display: grid; grid-template-columns: minmax(340px, .92fr) minmax(420px, 1.08fr); gap: 20px; align-items: start; }
    .panel { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
    .input-panel { padding: 24px; }
    .section-label { margin: 0 0 6px; color: var(--accent-deep); font-size: .78rem; font-weight: 800; letter-spacing: .04em; }
    .input-panel h3, .result-panel h3 { margin: 0; font-size: 1.2rem; }
    .input-panel > p { margin: 7px 0 20px; color: var(--muted); font-size: .92rem; }
    label { display: block; margin-bottom: 8px; font-weight: 700; }
    textarea { display: block; width: 100%; min-height: 132px; border: 1px solid #b9c9c2; border-radius: 10px; padding: 13px 14px; color: var(--ink); background: #fff; resize: vertical; outline: none; transition: border-color .16s ease, box-shadow .16s ease; }
    textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px #d8f2e8; }
    .field-row { display: flex; justify-content: space-between; gap: 12px; margin-top: 7px; color: var(--muted); font-size: .78rem; }
    .sample-title { margin: 22px 0 9px; color: var(--muted); font-size: .8rem; font-weight: 700; }
    .samples { display: flex; flex-wrap: wrap; gap: 8px; }
    .sample { border: 1px solid var(--line); border-radius: 999px; padding: 6px 10px; color: #30525e; background: #fff; font-size: .79rem; cursor: pointer; }
    .sample:hover, .sample:focus-visible { border-color: var(--accent); color: var(--accent-deep); outline: none; }
    .primary-button { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; width: 100%; margin-top: 22px; border: 0; border-radius: 10px; padding: 10px 18px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; transition: background .16s ease, transform .16s ease; }
    .primary-button:hover { background: var(--accent-deep); }
    .primary-button:active { transform: translateY(1px); }
    .primary-button:focus-visible { outline: 3px solid #8ee3c2; outline-offset: 2px; }
    .primary-button[disabled] { cursor: wait; opacity: .7; }
    .input-note { margin: 13px 0 0; color: var(--muted); font-size: .78rem; }
    .result-panel { min-height: 456px; overflow: hidden; }
    .result-head { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; padding: 22px 24px 18px; border-bottom: 1px solid var(--line); }
    .result-head p { margin: 5px 0 0; color: var(--muted); font-size: .86rem; }
    .result-status { display: inline-flex; align-items: center; gap: 6px; flex: none; padding: 6px 9px; border-radius: 999px; background: #edf1ef; color: #53656b; font-size: .78rem; font-weight: 700; }
    .result-status.confirmed { background: var(--mint); color: #056449; }
    .result-status.review { background: var(--amber); color: #8a5900; }
    .empty-state { display: grid; min-height: 360px; place-items: center; padding: 30px; color: var(--muted); text-align: center; }
    .empty-state span { display: grid; place-items: center; width: 48px; height: 48px; margin: 0 auto 12px; border-radius: 50%; color: var(--accent); background: var(--mint); font-size: 22px; }
    .empty-state p { margin: 0; max-width: 300px; }
    .result-body { padding: 24px; }
    .category-line { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding-bottom: 22px; }
    .category-name { margin: 0; font-size: clamp(1.45rem, 3vw, 2rem); line-height: 1.25; }
    .category-sub { margin: 5px 0 0; color: var(--muted); font-size: .86rem; }
    .category-id { padding: 6px 9px; border: 1px solid var(--line); border-radius: 7px; direction: ltr; color: var(--muted); background: #fafcfb; font-family: Consolas, monospace; font-size: .8rem; white-space: nowrap; }
    .decision-box { padding: 16px; border: 1px solid #cfe7dd; border-radius: 10px; background: #f4fbf7; }
    .decision-box h4, .alternative-wrap h4 { margin: 0 0 8px; font-size: .94rem; }
    .decision-summary { margin: 0; color: #30525e; font-size: .91rem; }
    .method-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 13px 0 0; }
    .method { display: inline-flex; align-items: center; gap: 6px; padding: 5px 8px; border-radius: 6px; font-size: .78rem; font-weight: 700; }
    .method.exact { color: #146142; background: #dff5ec; }
    .method.fuzzy { color: #8a5900; background: #fff1d7; }
    .method.semantic { color: #185779; background: #e3f1fb; }
    .method::before { content: "✓"; font-weight: 900; }
    .metrics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px; margin: 18px 0; overflow: hidden; border: 1px solid var(--line); border-radius: 10px; background: var(--line); }
    .metric { min-width: 0; padding: 11px 12px; background: #fff; }
    .metric dt { color: var(--muted); font-size: .75rem; }
    .metric dd { margin: 3px 0 0; color: var(--ink); font-weight: 800; font-size: .95rem; }
    .match-terms { display: flex; flex-wrap: wrap; gap: 7px; margin: 13px 0 0; }
    .match-term { padding: 4px 8px; border: 1px solid #c9ddd4; border-radius: 999px; color: #30525e; background: #fff; font-size: .78rem; }
    .alternative-wrap { padding-top: 18px; border-top: 1px solid var(--line); }
    .alternatives { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
    .alternative { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 9px 0; border-bottom: 1px solid #edf1ef; color: #3a535c; font-size: .88rem; }
    .alternative:last-child { border-bottom: 0; }
    .alternative-info { display: grid; gap: 2px; }
    .alternative-rank { color: var(--muted); direction: ltr; font-family: Consolas, monospace; font-size: .76rem; }
    .feedback-button { flex: none; border: 1px solid #9fc6b7; border-radius: 7px; padding: 6px 8px; color: #056449; background: #f4fbf7; font-size: .76rem; font-weight: 800; cursor: pointer; }
    .feedback-button:hover, .feedback-button:focus-visible { border-color: var(--accent); background: var(--mint); outline: none; }
    .feedback-button[disabled] { cursor: wait; opacity: .65; }
    .feedback-note { margin: 10px 0 0; color: var(--muted); font-size: .78rem; }
    .feedback-state { margin: 10px 0 0; padding: 9px 10px; border-right: 3px solid var(--accent); color: #30525e; background: var(--mint); font-size: .8rem; }
    .reason { margin: 16px 0 0; padding: 11px 12px; border-right: 3px solid #adc9bd; color: var(--muted); background: #fafcfb; font-size: .82rem; }
    details { margin-top: 18px; border-top: 1px solid var(--line); padding-top: 13px; }
    summary { cursor: pointer; color: #31515c; font-size: .83rem; font-weight: 700; }
    pre { max-height: 260px; margin: 12px 0 0; overflow: auto; direction: ltr; text-align: left; border-radius: 8px; padding: 12px; color: #dcebe5; background: #102833; font: .74rem/1.55 Consolas, monospace; }
    .alert { margin: 14px 24px 0; padding: 11px 12px; border-right: 3px solid #cf4b32; color: #8d3726; background: var(--danger); font-size: .84rem; }
    [hidden] { display: none !important; }
    @media (max-width: 840px) { .workspace { grid-template-columns: 1fr; } .intro { grid-template-columns: 1fr; } .catalog-stat { justify-self: start; } }
    @media (max-width: 560px) { .shell { width: min(100% - 24px, 1180px); padding-top: 18px; } .topbar { gap: 12px; } .service-state { max-width: 150px; white-space: normal; } .intro { padding: 22px 0; } .input-panel, .result-body { padding: 18px; } .result-head { padding: 18px; } .metrics { grid-template-columns: 1fr; } }
    @media (prefers-reduced-motion: no-preference) { .panel { animation: rise .26s ease-out both; } .result-body { animation: reveal .2s ease-out both; } @keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } } @keyframes reveal { from { opacity: 0; } to { opacity: 1; } } }
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">↢</div>
        <div>
          <p class="eyebrow">منصة دندن · خدمة مستقلة</p>
          <h1>مختبر تصنيف البضائع</h1>
        </div>
      </div>
      <div id="service-state" class="service-state" role="status">جاري التحقق من الخدمة</div>
    </header>

    <section class="intro" aria-labelledby="page-title">
      <div>
        <h2 id="page-title">اكتشف الصنف التصنيفي القابل للاختيار من وصف البضاعة الحر.</h2>
        <p>الخدمة تعيد <bdi>directGoodType</bdi> إذا كان الدليل كافياً، وتضعه داخل <bdi>rootGoodType</bdi> كسياق فقط. إذا ضعف الدليل تعيد مراجعة بدل ID مضلل.</p>
      </div>
      <div class="catalog-stat" id="catalog-stat"><strong>—</strong><span>جاري قراءة الكتالوج</span></div>
    </section>

    <div class="workspace">
      <section class="panel input-panel" aria-labelledby="input-title">
        <p class="section-label">إدخال تجريبي</p>
        <h3 id="input-title">وصف البضاعة</h3>
        <p>اكتب كما يكتب السائق: عربي، إنجليزي، لهجة أو خليط بينهما.</p>
        <form id="form">
          <label for="text">النص</label>
          <textarea id="text" name="text" maxlength="191" required aria-describedby="text-help">تلفزيون ذكي 65 بوصة</textarea>
          <div class="field-row"><span id="text-help">الحد الأقصى 191 حرفاً</span><span id="char-count">0 / 191</span></div>
          <p class="sample-title">أمثلة سريعة</p>
          <div class="samples" aria-label="أمثلة جاهزة">
            <button class="sample" type="button" data-sample="تلفزيون ذكي 65 بوصة">تلفزيون ذكي</button>
            <button class="sample" type="button" data-sample="حليب أطفال عضوي">حليب أطفال عضوي</button>
            <button class="sample" type="button" data-sample="مواد غزائيه">خطأ إملائي</button>
            <button class="sample" type="button" data-sample="kit kat">نص إنجليزي قصير</button>
          </div>
          <button id="submit-button" class="primary-button" type="submit">حلّل الصنف</button>
        </form>
        <p class="input-note">هذه شاشة عرض تجريبية؛ الربط الإنتاجي يستدعي <bdi>POST /v1/classify</bdi> من backend التطبيق.</p>
      </section>

      <section class="panel result-panel" aria-labelledby="result-title">
        <div class="result-head">
          <div>
            <p class="section-label">نتيجة التصنيف</p>
            <h3 id="result-title">القرار والدليل</h3>
            <p>تظهر المسارات التي دعمت الصنف الفائز فقط.</p>
          </div>
          <span id="result-status" class="result-status">بانتظار إدخال</span>
        </div>
        <div id="result-alert" class="alert" role="alert" hidden></div>
        <div id="empty-state" class="empty-state"><div><span aria-hidden="true">⌁</span><p>أدخل وصفاً ثم اضغط التحليل. سيظهر الصنف القابل للاختيار أو سبب المراجعة مع البدائل.</p></div></div>
        <div id="decision-card" class="result-body" hidden aria-live="polite">
          <div class="category-line">
            <div><h4 id="category-name" class="category-name">—</h4><p id="category-en" class="category-sub">—</p></div>
            <span id="category-id" class="category-id">ID —</span>
          </div>
          <div class="decision-box">
            <h4>مسار القرار</h4>
            <p id="decision-summary" class="decision-summary">—</p>
            <div id="method-list" class="method-list" aria-label="محركات البحث المستخدمة"></div>
            <div id="match-terms" class="match-terms" aria-label="الأسماء أو المصطلحات المطابقة"></div>
          </div>
          <dl class="metrics">
            <div class="metric"><dt>قوة أقوى دليل</dt><dd id="max-evidence">—</dd></div>
            <div class="metric"><dt>فارق المرشح الأول</dt><dd id="score-margin">—</dd></div>
            <div class="metric"><dt>لغة النص</dt><dd id="language">—</dd></div>
            <div class="metric"><dt>زمن الاستجابة</dt><dd id="latency">—</dd></div>
          </dl>
          <div class="alternative-wrap">
            <h4>بدائل مقترحة</h4>
            <ol id="alternatives" class="alternatives"></ol>
            <p class="feedback-note">إذا كانت النتيجة غير صحيحة، اختر الصنف الصحيح لتسجيل التصحيح في سجل التعلّم التجريبي.</p>
            <p id="feedback-state" class="feedback-state" role="status" hidden></p>
          </div>
          <p id="reason" class="reason">—</p>
          <details><summary>عرض الاستجابة التقنية الكاملة</summary><pre id="raw-result"></pre></details>
        </div>
      </section>
    </div>
  </main>
  <script>
    const textInput = document.getElementById("text");
    const form = document.getElementById("form");
    const submitButton = document.getElementById("submit-button");
    const charCount = document.getElementById("char-count");
    const serviceState = document.getElementById("service-state");
    const catalogStat = document.getElementById("catalog-stat");
    const emptyState = document.getElementById("empty-state");
    const decisionCard = document.getElementById("decision-card");
    const resultAlert = document.getElementById("result-alert");
    const resultStatus = document.getElementById("result-status");
    const feedbackState = document.getElementById("feedback-state");
    let lastResult = null;
    let feedbackSubmitting = false;

    const methodLabels = {
      EXACT: "تطابق حرفي",
      LEXICAL_VARIANT: "معالجة صرفية / لفظية",
      FUZZY: "بحث تقريبي / إملائي",
      SEMANTIC: "بحث دلالي بالـ Embedding"
    };
    const reasonLabels = {
      EXACT: "تمت المطابقة بشكل مباشر مع اسم موجود في الكتالوج.",
      LEXICAL_VARIANT: "تمت المطابقة بعد معالجة صرفية أو لفظية عامة على النص.",
      HYBRID_STRONG: "اتفق البحث التقريبي والبحث الدلالي بقوة كافية لإرجاع النتيجة دون مراجعة.",
      AMBIGUOUS: "هناك أكثر من صنف قريب أو مصطلح مشترك؛ يلزم تأكيد بشري.",
      LOW_EVIDENCE: "يوجد مرشح أول، لكن الدليل أو الفارق عن البدائل غير كافٍ للثقة النهائية.",
      UNSUPPORTED_LANGUAGE: "اللغة خارج العربية أو الإنجليزية أو النص المختلط؛ يلزم تأكيد بشري.",
      MULTI_CATEGORY: "النص يبدو أنه يتضمن أكثر من صنف رئيسي؛ يلزم تقسيمه أو تأكيده.",
      EMBEDDING_UNAVAILABLE: "الموديل الدلالي غير متاح، لذا لا يمكن اعتماد النتيجة دون مراجعة."
    };
    const languageLabels = { AR: "عربي", EN: "إنجليزي", MIXED: "مختلط", OTHER: "أخرى" };
    const inputQualityMessage = "أدخل وصفاً مفهوماً للبضاعة من 3 أحرف على الأقل؛ لا تُدخل أرقاماً فقط أو حروفاً مكررة أو عشوائية.";
    const inputTokenPattern = /[a-z]+|[\u0621-\u064a]+/g;
    const ignoredConnectors = new Set(["و"]);

    function setText(id, value) { document.getElementById(id).textContent = value; }
    function updateCount() { charCount.textContent = `${textInput.value.length} / 191`; }
    function preflightInputError(value) {
      const lowered = value.toLowerCase();
      const tokens = lowered.match(inputTokenPattern) || [];
      if (!/\\p{L}/u.test(value)) return inputQualityMessage;
      // Let languages outside Arabic/English reach the server's review path.
      if (!tokens.length) return null;
      const contentTokens = tokens.filter((token) => !ignoredConnectors.has(token));
      if (!contentTokens.length || contentTokens.some((token) => token.length < 3)) return inputQualityMessage;
      const isRepeated = (token) => {
        const highestCount = Math.max(...Array.from(new Set(token), (char) => token.split(char).length - 1));
        return /(.)\\1{2,}/.test(token) || highestCount / token.length >= 0.6;
      };
      // The server has the catalog and local lexical evidence needed to judge
      // keyboard-like strings safely. The demo only rejects unambiguous noise.
      return contentTokens.some((token) => isRepeated(token)) ? inputQualityMessage : null;
    }
    function requestId() { return window.crypto?.randomUUID?.() || `demo-${Date.now()}-${Math.random().toString(16).slice(2)}`; }
    function clearChildren(element) { while (element.firstChild) element.removeChild(element.firstChild); }
    function appendBadge(container, method, evidence) {
      const badge = document.createElement("span");
      badge.className = `method ${method.toLowerCase()}`;
      const score = evidence ? ` · ${Math.round(evidence.score * 100)}%` : "";
      badge.textContent = `${methodLabels[method] || method}${score}`;
      if (evidence) badge.title = `الدليل: ${evidence.matchedTerm}`;
      container.appendChild(badge);
    }
    function decisionText(methods) {
      const hasSemantic = methods.includes("SEMANTIC");
      const hasFuzzy = methods.includes("FUZZY");
      const hasExact = methods.includes("EXACT");
      if (hasExact) return "اعتمد القرار على تطابق حرفي واضح داخل الكتالوج؛ لم يحتج إلى بحث دلالي أو تقريبي.";
      if (methods.includes("LEXICAL_VARIANT")) return "اعتمد القرار على معالجة لفظية عامة ثم وجد دليلاً واضحاً داخل الكتالوج.";
      if (hasSemantic && hasFuzzy) return "تم دمج البحث الدلالي مع البحث التقريبي؛ كل منهما دعم الصنف الفائز.";
      if (hasSemantic) return "تم استخدام البحث الدلالي بالـ Embedding لإيجاد الصنف الأقرب من المعنى.";
      if (hasFuzzy) return "تم استخدام البحث التقريبي لمعالجة اختلاف الصياغة أو الخطأ الإملائي.";
      return "لم يصل أثر كافٍ للمحرك الذي دعم القرار.";
    }
    function renderTerms(terms) {
      const container = document.getElementById("match-terms");
      clearChildren(container);
      for (const term of terms) {
        const item = document.createElement("span");
        item.className = "match-term";
        item.textContent = term;
        container.appendChild(item);
      }
    }
    function renderAlternatives(alternatives) {
      const list = document.getElementById("alternatives");
      clearChildren(list);
      for (const alternative of alternatives) {
        const item = document.createElement("li");
        item.className = "alternative";
        const info = document.createElement("div");
        info.className = "alternative-info";
        const name = document.createElement("span");
        name.textContent = alternative.nameAr;
        const rank = document.createElement("span");
        rank.className = "alternative-rank";
        rank.textContent = `#${alternative.rank} · ID ${alternative.id}`;
        const select = document.createElement("button");
        select.className = "feedback-button";
        select.type = "button";
        select.textContent = "اختيار هذا الصنف";
        select.addEventListener("click", () => submitFeedback(alternative));
        info.append(name, rank);
        item.append(info, select);
        list.appendChild(item);
      }
    }
    function renderResult(data) {
      lastResult = data;
      const signals = data.matchSignals;
      const methods = signals.methods || [];
      const direct = data.directGoodType;
      emptyState.hidden = true;
      decisionCard.hidden = false;
      setText("category-name", direct ? direct.nameAr : "لا توجد نتيجة مؤكدة");
      setText(
        "category-en",
        direct
          ? `${direct.nameEn || ""} · root ${direct.rootId || "—"}`
          : "الدليل غير كافٍ لإرجاع good_type نهائي"
      );
      setText("category-id", direct ? `ID ${direct.id}` : "NO DECISION");
      setText("decision-summary", decisionText(methods));
      const methodsContainer = document.getElementById("method-list");
      clearChildren(methodsContainer);
      const evidenceByMethod = new Map((signals.evidence || []).map((item) => [item.method, item]));
      methods.forEach((method) => appendBadge(methodsContainer, method, evidenceByMethod.get(method)));
      renderTerms(signals.matchedTerms || []);
      setText("max-evidence", `${Math.round((signals.maxEvidence || 0) * 100)}%`);
      setText("score-margin", signals.scoreMargin == null ? "مرشح واحد" : signals.scoreMargin.toFixed(4));
      setText("language", languageLabels[data.language] || data.language);
      setText("latency", `${data.latencyMs} ms`);
      renderAlternatives(data.alternatives || []);
      feedbackState.hidden = true;
      setText("reason", reasonLabels[data.reason] || data.reason);
      setText("raw-result", JSON.stringify(data, null, 2));
      const review = Boolean(data.requiresReview);
      resultStatus.className = `result-status ${review ? "review" : "confirmed"}`;
      resultStatus.textContent = review ? "تحتاج مراجعة" : "نتيجة مؤكدة";
    }
    async function submitFeedback(category) {
      if (!lastResult || feedbackSubmitting) return;
      feedbackSubmitting = true;
      const buttons = [...document.querySelectorAll(".feedback-button")];
      buttons.forEach((button) => { button.disabled = true; });
      feedbackState.hidden = false;
      feedbackState.textContent = "جاري تسجيل التصحيح…";
      try {
        const response = await fetch(`/demo/classifications/${encodeURIComponent(lastResult.requestId)}/feedback`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            feedbackId: requestId(),
            selectedGoodTypeId: category.id,
            source: "DEMO"
          })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data?.error?.message || "تعذّر تسجيل التصحيح");
        feedbackState.textContent = `تم تسجيل اختيار «${data.selectedGoodType.nameAr}» للتدقيق والتحسين لاحقاً.`;
      } catch (error) {
        feedbackState.textContent = error instanceof Error ? error.message : "تعذّر تسجيل التصحيح";
        buttons.forEach((button) => { button.disabled = false; });
      } finally {
        feedbackSubmitting = false;
      }
    }
    function showError(message) {
      resultAlert.textContent = message;
      resultAlert.hidden = false;
      resultStatus.className = "result-status review";
      resultStatus.textContent = "تعذّر التصنيف";
    }
    function invalidateResult() {
      if (decisionCard.hidden) return;
      lastResult = null;
      decisionCard.hidden = true;
      emptyState.hidden = false;
      resultAlert.hidden = true;
      feedbackState.hidden = true;
      resultStatus.className = "result-status";
      resultStatus.textContent = "تحتاج تحليلاً جديداً";
    }
    function renderCatalogStat(data) {
      clearChildren(catalogStat);
      const rootCount = document.createElement("strong");
      rootCount.textContent = data.selectableGoodTypeCount || data.rootCount;
      const terms = document.createElement("span");
      terms.textContent = `صنف قابل للاختيار · ${data.goodTypeCount || "—"} نوع · ${data.termCount} مصطلح بحث`;
      catalogStat.append(rootCount, terms);
    }
    async function loadHealth() {
      try {
        const response = await fetch("/health");
        const data = await response.json();
        if (!response.ok || data.status !== "ok") throw new Error("الخدمة غير جاهزة");
        const semanticReady = data.modelVersion !== "semantic-disabled";
        serviceState.className = `service-state ${semanticReady ? "ready" : "warning"}`;
        serviceState.textContent = semanticReady ? "البحث الدلالي جاهز" : "البحث الدلالي غير مفعّل";
        renderCatalogStat(data);
      } catch (_) {
        serviceState.className = "service-state error";
        serviceState.textContent = "الخدمة غير متاحة";
        catalogStat.textContent = "تعذّر قراءة حالة الكتالوج";
      }
    }
    document.querySelectorAll("[data-sample]").forEach((button) => {
      button.addEventListener("click", () => { textInput.value = button.dataset.sample || ""; updateCount(); textInput.focus(); });
    });
    textInput.addEventListener("input", () => { updateCount(); invalidateResult(); });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      resultAlert.hidden = true;
      const inputError = preflightInputError(textInput.value);
      if (inputError) {
        showError(inputError);
        return;
      }
      submitButton.disabled = true;
      submitButton.textContent = "جاري التحليل…";
      resultStatus.className = "result-status";
      resultStatus.textContent = "جاري التحليل";
      try {
        const response = await fetch("/demo/classify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ requestId: requestId(), text: textInput.value })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data?.error?.message || "تعذّر إكمال الطلب");
        renderResult(data);
      } catch (error) {
        showError(error instanceof Error ? error.message : "تعذّر الاتصال بالخدمة");
      } finally {
        submitButton.disabled = false;
        submitButton.textContent = "حلّل الصنف";
      }
    });
    updateCount();
    loadHealth();
  </script>
</body>
</html>"""
