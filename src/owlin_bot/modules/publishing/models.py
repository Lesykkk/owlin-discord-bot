"""Data models for the publishing module."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PublishRequest:
    """Data required to publish an embed."""

    source_guild_id: int
    source_channel_id: int
    target_guild_id: int
    target_channel_id: int
    content: str
