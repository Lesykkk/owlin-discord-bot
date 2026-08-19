from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest
from owlin_bot.modules.publishing.commands import PublishingCommands
class FakePublishingService:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.requests = []

    async def publish(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error


def make_context(*, guild_id: int | None = 42):
    return SimpleNamespace(
        guild=SimpleNamespace(id=guild_id) if guild_id is not None else None,
        channel=SimpleNamespace(id=10),
        send=AsyncMock(),
    )


def make_target():
    return SimpleNamespace(id=99, guild=SimpleNamespace(id=42))


@pytest.mark.asyncio
async def test_handler_passes_request_without_deleting_source_message():
    service = FakePublishingService()
    publishing_commands = PublishingCommands(service)
    context = make_context()

    await publishing_commands.publish(context, make_target(), content="**Hello**")

    assert len(service.requests) == 1
    request = service.requests[0]
    assert request.source_channel_id == 10
    assert request.target_channel_id == 99
    assert request.content == "**Hello**"


@pytest.mark.asyncio
async def test_handler_propagates_publish_error():
    service = FakePublishingService(RuntimeError("send failed"))
    publishing_commands = PublishingCommands(service)
    context = make_context()

    with pytest.raises(RuntimeError, match="send failed"):
        await publishing_commands.publish(context, make_target(), content="Hello")


@pytest.mark.asyncio
async def test_handler_rejects_direct_message():
    service = FakePublishingService()
    publishing_commands = PublishingCommands(service)
    context = make_context(guild_id=None)

    await publishing_commands.publish(context, make_target(), content="Hello")

    assert service.requests == []
