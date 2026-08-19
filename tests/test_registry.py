from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from owlin_bot.app.registry import register
from owlin_bot.integrations.discord_client import DiscordClient
from owlin_bot.app.settings import Settings
from owlin_bot.modules.publishing.commands import PublishingCommands


@pytest.mark.asyncio
async def test_register_registers_message_events_and_commands():
    bot = SimpleNamespace(
        add_listener=Mock(),
        add_cog=AsyncMock(),
        event=Mock(side_effect=lambda callback: callback),
    )
    settings = Settings(discord_token="test-token", restricted_channel_id=7)
    discord_client = DiscordClient(SimpleNamespace())

    await register(bot, settings, discord_client)

    assert bot.add_listener.call_count == 3
    bot.add_cog.assert_awaited_once()
    assert isinstance(bot.add_cog.call_args.args[0], PublishingCommands)
    bot.event.assert_called_once()
