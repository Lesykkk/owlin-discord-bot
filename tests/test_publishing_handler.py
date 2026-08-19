from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest
from owlin_bot.app.settings import Settings
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


def make_commands(service):
    settings = Settings(
        discord_token="test-token",
        restricted_channel_id=7,
        publish_command_channel_id=10,
    )
    return PublishingCommands(settings, service)


@pytest.mark.asyncio
async def test_handler_passes_request_without_deleting_source_message():
    service = FakePublishingService()
    publishing_commands = make_commands(service)
    context = make_context()

    await publishing_commands.publish.callback(
        publishing_commands,
        context,
        make_target(),
        content="**Hello**",
    )

    assert len(service.requests) == 1
    request = service.requests[0]
    assert request.source_channel_id == 10
    assert request.target_channel_id == 99
    assert request.content == "**Hello**"


@pytest.mark.asyncio
async def test_handler_propagates_publish_error():
    service = FakePublishingService(RuntimeError("send failed"))
    publishing_commands = make_commands(service)
    context = make_context()

    with pytest.raises(RuntimeError, match="send failed"):
        await publishing_commands.publish.callback(
            publishing_commands,
            context,
            make_target(),
            content="Hello",
        )


@pytest.mark.asyncio
async def test_handler_rejects_direct_message():
    service = FakePublishingService()
    publishing_commands = make_commands(service)
    context = make_context(guild_id=None)

    await publishing_commands.publish.callback(
        publishing_commands,
        context,
        make_target(),
        content="Hello",
    )

    assert service.requests == []
