from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from owlin_bot.app.composition import configure_error_handling, configure_lifecycle
from owlin_bot.app.tree import OwlinCommandTree
from owlin_bot.integrations.discord_client import DiscordClient


def test_configure_error_handling_wires_every_surface():
    bot = SimpleNamespace(add_listener=Mock(), event=Mock(side_effect=lambda callback: callback))
    tree = OwlinCommandTree.__new__(OwlinCommandTree)
    discord_client = DiscordClient(SimpleNamespace())

    configure_error_handling(bot, tree, discord_client)

    assert bot.add_listener.call_count == 1
    bot.event.assert_called_once()
    assert tree.handler is not None


@pytest.mark.asyncio
async def test_configure_lifecycle_registers_before_invoke_and_on_ready():
    bot = SimpleNamespace(before_invoke=Mock(), add_listener=Mock())

    configure_lifecycle(bot)

    bot.before_invoke.assert_called_once()
    bot.add_listener.assert_called_once()
