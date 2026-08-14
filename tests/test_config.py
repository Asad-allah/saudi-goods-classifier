from app.core.config import get_settings


def test_demo_endpoint_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("DANDAN_DEMO_ENABLED", raising=False)

    assert get_settings().demo_enabled is False


def test_demo_allowed_origins_are_parsed_from_csv(monkeypatch) -> None:
    monkeypatch.setenv(
        "DANDAN_DEMO_ALLOWED_ORIGINS",
        " https://demo.example.com,https://review.example.com ",
    )

    assert get_settings().demo_allowed_origins == (
        "https://demo.example.com",
        "https://review.example.com",
    )


def test_input_validation_can_be_disabled_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("DANDAN_INPUT_VALIDATION_ENABLED", "false")

    assert get_settings().input_validation_enabled is False
