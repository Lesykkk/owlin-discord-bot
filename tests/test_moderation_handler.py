from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from owlin_bot.handlers.moderation_handler import ModerationHandler


@dataclass
class FakeAuthor:
    id: int
    bot: bool = False


@dataclass
class FakeGuild:
    id: int
    owner_id: int


@dataclass
class FakeChannel:
    id: int


@dataclass
class FakeMessage:
    author: FakeAuthor
    guild: FakeGuild | None
    channel: FakeChannel
    created_at: datetime


class FakeModerationService:
    def __init__(self) -> None:
        self.events = []

    async def handle_message(self, event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_handler_maps_discord_message_to_service_event():
    service = FakeModerationService()
    handler = ModerationHandler(service)
    created_at = datetime(2026, 8, 19, 12, 5, tzinfo=timezone.utc)

    await handler.handle_message(
        FakeMessage(
            author=FakeAuthor(id=99),
            guild=FakeGuild(id=42, owner_id=100),
            channel=FakeChannel(id=7),
            created_at=created_at,
        )
    )

    assert len(service.events) == 1
    event = service.events[0]
    assert event.guild_id == 42
    assert event.channel_id == 7
    assert event.author_id == 99
    assert event.author_is_bot is False
    assert event.author_is_server_owner is False
    assert event.author_is_administrator is False
    assert event.created_at == created_at
