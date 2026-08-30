from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from owlin_bot.app.services import Services
from owlin_bot.app.settings import Settings
from owlin_bot.modules.moderation.setup import setup


@pytest.mark.asyncio
async def test_setup_builds_service_registers_listener_and_stores_it():
    settings = Settings(discord_token="test-token", restricted_channel_id=7)
    bot = SimpleNamespace(
        settings=settings,
        discord_client=SimpleNamespace(),
        services=Services(),
        add_listener=Mock(),
    )

    await setup(bot)

    bot.add_listener.assert_called_once()
    assert bot.services.moderation is not None
