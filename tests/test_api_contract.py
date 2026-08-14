import asyncio
import json

import httpx

from app.catalog.importer import build_catalog
from app.catalog.models import GoodType
from app.classifier.events import JsonlEventLogger
from app.classifier.service import RootCategoryClassifier
from app.core.config import Settings
from app.main import app


def _request(method: str, path: str, **kwargs) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send())


def _install_test_state(tmp_path):
    catalog = build_catalog(
        [
            GoodType(12, "مواد غذائية", "Food Items", (), None),
            GoodType(14, "سلع جافة", "Dry FMCG", ("كيت كات",), 12),
            GoodType(141, "النفايات", "Waste material", (), None),
        ],
        source_sha256="fixture",
        version="test",
    )
    app.state.settings = Settings(
        app_name="test",
        api_key="secret",
        api_key_header="X-API-Key",
        catalog_source="",
        catalog_artifact="",
        catalog_version="test",
        event_log_path=str(tmp_path / "events.jsonl"),
        semantic_model_name="disabled",
        enable_semantic=False,
        max_text_length=191,
        demo_enabled=True,
    )
    app.state.event_logger = JsonlEventLogger(str(tmp_path / "events.jsonl"))
    app.state.classifier = RootCategoryClassifier(catalog)


def test_classify_requires_api_key(tmp_path) -> None:
    _install_test_state(tmp_path)
    response = _request(
        "POST",
        "/v1/classify",
        json={"requestId": "1", "text": "كيت كات"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_classify_response_shape(tmp_path) -> None:
    _install_test_state(tmp_path)
    response = _request(
        "POST",
        "/v1/classify",
        headers={"X-API-Key": "secret"},
        json={"requestId": "1", "text": "كيت كات"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["directGoodType"] == {
        "id": 14,
        "nameAr": "سلع جافة",
        "nameEn": "Dry FMCG",
        "rank": 1,
        "parentId": 12,
        "rootId": 12,
        "isSelectable": True,
    }
    assert data["rootGoodType"] == {
        "id": 12,
        "nameAr": "مواد غذائية",
        "nameEn": "Food Items",
        "rank": 1,
        "parentId": None,
        "rootId": 12,
        "isSelectable": False,
    }
    assert data["reason"] == "EXACT"
    assert data["normalizedText"] == "كيت كات"
    assert data["matchSignals"] == {
        "methods": ["EXACT"],
        "evidence": [
            {"method": "EXACT", "matchedTerm": "كيت كات", "score": 1.0, "rank": 1}
        ],
        "matchedTerms": ["كيت كات"],
        "maxEvidence": 1.0,
        "scoreMargin": None,
    }


def test_classify_returns_the_real_normalized_text(tmp_path) -> None:
    _install_test_state(tmp_path)

    response = _request(
        "POST",
        "/v1/classify",
        headers={"X-API-Key": "secret"},
        json={"requestId": "normalized", "text": "  كِــيت   كات!  "},
    )

    assert response.status_code == 200
    assert response.json()["normalizedText"] == "كيت كات"


def test_validation_error_for_empty_text(tmp_path) -> None:
    _install_test_state(tmp_path)
    response = _request(
        "POST",
        "/v1/classify",
        headers={"X-API-Key": "secret"},
        json={"requestId": "1", "text": ""},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_classify_rejects_meaningless_text_before_search(tmp_path) -> None:
    _install_test_state(tmp_path)
    response = _request(
        "POST",
        "/v1/classify",
        headers={"X-API-Key": "secret"},
        json={"requestId": "noise", "text": "123456"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "INPUT_NOT_MEANINGFUL",
                "message": "أدخل وصفاً مفهوماً للبضاعة من 3 أحرف على الأقل؛ لا تُدخل أرقاماً فقط أو حروفاً مكررة أو عشوائية.",
            "details": {"validationReason": "NO_LETTERS"},
        }
    }


def test_classify_explains_which_quality_rule_rejected_input(tmp_path) -> None:
    _install_test_state(tmp_path)

    response = _request(
        "POST",
        "/v1/classify",
        headers={"X-API-Key": "secret"},
        json={"requestId": "repeated", "text": "سسسسسس"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["details"] == {
        "validationReason": "REPEATED_NOISE"
    }


def test_classify_requires_context_for_a_single_unknown_brand_like_word(tmp_path) -> None:
    _install_test_state(tmp_path)
    response = _request(
        "POST",
        "/v1/classify",
        headers={"X-API-Key": "secret"},
        json={"requestId": "brand", "text": "qazmori"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "INSUFFICIENT_CONTEXT",
            "message": "اكتب نوع البضاعة مع العلامة أو الموديل، مثلاً: حليب نيدو أو تلفزيون سامسونج.",
            "details": {"validationReason": "INSUFFICIENT_CONTEXT"},
        }
    }


def test_demo_page_explains_the_decision_path(tmp_path) -> None:
    _install_test_state(tmp_path)
    response = _request("GET", "/")

    assert response.status_code == 200
    assert "مسار القرار" in response.text
    assert "matchSignals" in response.text
    assert "/demo/classify" in response.text
    assert "/demo/classifications/" in response.text
    assert "submitFeedback" in response.text
    assert "invalidateResult" in response.text
    assert "preflightInputError" in response.text
    assert "isKeyboardMash" not in response.text


def test_demo_accepts_local_visual_companion_origin(tmp_path) -> None:
    """A local engineering prototype can read real demo classifications."""
    _install_test_state(tmp_path)

    response = _request(
        "OPTIONS",
        "/demo/classify",
        headers={
            "Origin": "http://localhost:52345",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:52345"
    assert "POST" in response.headers["access-control-allow-methods"]


def test_demo_cors_rejects_non_local_origin(tmp_path) -> None:
    _install_test_state(tmp_path)

    response = _request(
        "OPTIONS",
        "/demo/classify",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_verified_feedback_records_a_root_category_correction(tmp_path) -> None:
    _install_test_state(tmp_path)
    classified = _request(
        "POST",
        "/v1/classify",
        headers={"X-API-Key": "secret"},
        json={"requestId": "trash-bag", "text": "كيت كات"},
    )
    assert classified.status_code == 200

    response = _request(
        "POST",
        "/v1/classifications/trash-bag/feedback",
        headers={"X-API-Key": "secret"},
        json={
            "feedbackId": "feedback-trash-bag-1",
            "selectedGoodTypeId": 141,
            "source": "OPERATOR_REVIEW",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "feedbackId": "feedback-trash-bag-1",
        "requestId": "trash-bag",
        "selectedGoodType": {
            "id": 141,
            "nameAr": "النفايات",
            "nameEn": "Waste material",
            "rank": 1,
            "parentId": None,
            "rootId": 141,
            "isSelectable": True,
        },
        "trainingEligibility": "CANDIDATE_AFTER_VALIDATION",
    }

    events = [
        json.loads(line)
        for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert events[-1]["eventType"] == "CLASSIFICATION_FEEDBACK"
    assert events[-1]["selectedGoodTypeId"] == 141
    assert events[-1]["selectedRootGoodTypeId"] == 141
    assert events[-1]["trainingEligibility"] == "CANDIDATE_AFTER_VALIDATION"


def test_feedback_can_follow_a_service_restart(tmp_path) -> None:
    _install_test_state(tmp_path)
    headers = {"X-API-Key": "secret"}
    classified = _request(
        "POST",
        "/v1/classify",
        headers=headers,
        json={"requestId": "restart-safe", "text": "كيت كات"},
    )
    assert classified.status_code == 200

    app.state.event_logger = JsonlEventLogger(str(tmp_path / "events.jsonl"))
    response = _request(
        "POST",
        "/v1/classifications/restart-safe/feedback",
        headers=headers,
        json={
            "feedbackId": "feedback-after-restart",
            "selectedGoodTypeId": 141,
            "source": "OPERATOR_REVIEW",
        },
    )

    assert response.status_code == 200


def test_feedback_rejects_a_parent_or_unknown_category_id(tmp_path) -> None:
    _install_test_state(tmp_path)

    response = _request(
        "POST",
        "/v1/classifications/request-1/feedback",
        headers={"X-API-Key": "secret"},
        json={
            "feedbackId": "feedback-invalid-root",
            "selectedGoodTypeId": 12,
            "source": "OPERATOR_REVIEW",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "GOOD_TYPE_NOT_SELECTABLE"


def test_feedback_rejects_an_unknown_classification_request(tmp_path) -> None:
    _install_test_state(tmp_path)

    response = _request(
        "POST",
        "/v1/classifications/request-that-was-never-classified/feedback",
        headers={"X-API-Key": "secret"},
        json={
            "feedbackId": "feedback-orphan",
            "selectedGoodTypeId": 141,
            "source": "OPERATOR_REVIEW",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CLASSIFICATION_REQUEST_UNKNOWN"
    assert not (tmp_path / "events.jsonl").exists()


def test_feedback_id_is_idempotent_and_rejects_conflicting_reuse(tmp_path) -> None:
    _install_test_state(tmp_path)
    payload = {
        "feedbackId": "feedback-idempotent",
        "selectedGoodTypeId": 141,
        "source": "OPERATOR_REVIEW",
    }
    headers = {"X-API-Key": "secret"}
    classified = _request(
        "POST",
        "/v1/classify",
        headers=headers,
        json={"requestId": "request-1", "text": "كيت كات"},
    )
    assert classified.status_code == 200

    first = _request(
        "POST",
        "/v1/classifications/request-1/feedback",
        headers=headers,
        json=payload,
    )
    second = _request(
        "POST",
        "/v1/classifications/request-1/feedback",
        headers=headers,
        json=payload,
    )
    conflicting = _request(
        "POST",
        "/v1/classifications/request-1/feedback",
        headers=headers,
        json={**payload, "selectedGoodTypeId": 14},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert conflicting.status_code == 409
    assert conflicting.json()["error"]["code"] == "FEEDBACK_ID_CONFLICT"
    events = [
        json.loads(line)
        for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [event["eventType"] for event in events] == [
        "CLASSIFICATION",
        "CLASSIFICATION_FEEDBACK",
    ]
