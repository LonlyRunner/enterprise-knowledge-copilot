import pytest

from app.core.config import Settings


def test_production_settings_fail_closed_without_secrets():
    settings = Settings(environment="production", auth_enabled=False)
    with pytest.raises(ValueError):
        settings.validate_runtime()


def test_production_settings_accept_strong_secrets():
    settings = Settings(
        environment="production",
        auth_enabled=True,
        jwt_secret="j" * 40,
        metrics_auth_token="m" * 40,
    )
    settings.validate_runtime()
