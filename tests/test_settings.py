from __future__ import annotations

import pytest

import owlin_bot.settings as settings_module
from owlin_bot.settings import SettingsError


def prepare_environment(monkeypatch, *, token: str | None = "test-token") -> None:
    monkeypatch.setattr(settings_module, "load_dotenv", lambda: None)
    monkeypatch.setattr(settings_module, "WATCHED_CHANNEL_ID", 123)
    if token is None:
        monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    else:
        monkeypatch.setenv("DISCORD_TOKEN", token)


def test_settings_load_only_secret_from_environment(monkeypatch):
    prepare_environment(monkeypatch)

    settings = settings_module.Settings.from_environment()

    assert settings.discord_token == "test-token"
    assert settings.watched_channel_id == 123
    assert settings.cleanup_window_seconds == 300


def test_settings_require_discord_token(monkeypatch):
    prepare_environment(monkeypatch, token=None)

    with pytest.raises(SettingsError, match="DISCORD_TOKEN"):
        settings_module.Settings.from_environment()


def test_settings_require_channel_id_in_code(monkeypatch):
    prepare_environment(monkeypatch)
    monkeypatch.setattr(settings_module, "WATCHED_CHANNEL_ID", 0)

    with pytest.raises(SettingsError, match="WATCHED_CHANNEL_ID"):
        settings_module.Settings.from_environment()
