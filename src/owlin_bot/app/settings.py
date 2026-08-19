"""Load secret and application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from owlin_bot.app.constants import (
    CLEANUP_WINDOW_SECONDS,
    PUBLISH_COMMAND_CHANNEL_ID,
    WATCHED_CHANNEL_ID,
)


class SettingsError(ValueError):
    """Raised when required application settings are invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings required by the bot."""

    discord_token: str
    watched_channel_id: int
    publish_command_channel_id: int = PUBLISH_COMMAND_CHANNEL_ID
    cleanup_window_seconds: int = CLEANUP_WINDOW_SECONDS

    @classmethod
    def from_environment(cls) -> Settings:
        """Create settings from the environment and application constants."""
        load_dotenv()

        token = os.getenv("DISCORD_TOKEN", "").strip()
        if not token or token == "replace-with-your-discord-bot-token":
            raise SettingsError("DISCORD_TOKEN must contain a real Discord bot token")
        if WATCHED_CHANNEL_ID <= 0:
            raise SettingsError("Set WATCHED_CHANNEL_ID in app/constants.py")

        return cls(
            discord_token=token,
            watched_channel_id=WATCHED_CHANNEL_ID,
        )
