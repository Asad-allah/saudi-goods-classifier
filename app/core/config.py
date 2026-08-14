from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency exists in normal installs
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _csv_env(name: str) -> tuple[str, ...]:
    return tuple(
        item.strip()
        for item in os.getenv(name, "").split(",")
        if item.strip()
    )


def _default_catalog_source() -> str:
    explicit = os.getenv("DANDAN_CATALOG_SOURCE")
    if explicit:
        return explicit

    candidates = [
        Path("data") / "sub_db.sql",
        Path.home() / "Downloads" / "Telegram Desktop" / "sub_db.sql",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return ""


@dataclass(frozen=True)
class Settings:
    app_name: str
    api_key: str
    api_key_header: str
    catalog_source: str
    catalog_artifact: str
    catalog_version: str
    event_log_path: str
    semantic_model_name: str
    enable_semantic: bool
    max_text_length: int
    demo_enabled: bool
    demo_allowed_origins: tuple[str, ...] = ()
    input_validation_enabled: bool = True


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("DANDAN_APP_NAME", "Dandan Root Category Classifier"),
        api_key=os.getenv("DANDAN_API_KEY", "dev-dandan-key"),
        api_key_header=os.getenv("DANDAN_API_KEY_HEADER", "X-API-Key"),
        catalog_source=_default_catalog_source(),
        catalog_artifact=os.getenv("DANDAN_CATALOG_ARTIFACT", ""),
        catalog_version=os.getenv("DANDAN_CATALOG_VERSION", ""),
        event_log_path=os.getenv(
            "DANDAN_EVENT_LOG_PATH",
            str(Path("storage") / "events" / "classification_events.jsonl"),
        ),
        semantic_model_name=os.getenv(
            "DANDAN_SEMANTIC_MODEL", "intfloat/multilingual-e5-small"
        ),
        enable_semantic=_bool_env("DANDAN_ENABLE_SEMANTIC", False),
        max_text_length=int(os.getenv("DANDAN_MAX_TEXT_LENGTH", "191")),
        demo_enabled=_bool_env("DANDAN_DEMO_ENABLED", False),
        demo_allowed_origins=_csv_env("DANDAN_DEMO_ALLOWED_ORIGINS"),
        input_validation_enabled=_bool_env(
            "DANDAN_INPUT_VALIDATION_ENABLED",
            True,
        ),
    )
