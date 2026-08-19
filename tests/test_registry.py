from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

from owlin_bot.app.registry import register
from owlin_bot.integrations.discord_client import DiscordClient
from owlin_bot.app.settings import Settings


def test_register_registers_message_events_and_commands():
    bot = SimpleNamespace(
        add_listener=Mock(),
        command=Mock(side_effect=lambda **kwargs: lambda callback: callback),
        event=Mock(side_effect=lambda callback: callback),
    )
    settings = Settings(discord_token="test-token", restricted_channel_id=7)
    discord_client = DiscordClient(SimpleNamespace())

    register(bot, settings, discord_client)

    assert bot.add_listener.call_count == 3
    bot.command.assert_called_once()
    assert bot.command.call_args.kwargs["name"] == "publish"
    assert len(bot.command.call_args.kwargs["checks"]) == 3
    bot.event.assert_called_once()
