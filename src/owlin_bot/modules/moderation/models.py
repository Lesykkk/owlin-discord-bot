"""Data models for the moderation module."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MessageEvent:
    """Facts extracted from a Discord message."""

    message_id: int
    guild_id: int | None
    channel_id: int
    author_id: int
    author_is_bot: bool
    author_is_server_owner: bool
    author_is_administrator: bool
    created_at: datetime
