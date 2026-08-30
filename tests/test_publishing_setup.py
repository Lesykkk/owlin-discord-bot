from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from owlin_bot.app.services import Services
from owlin_bot.app.settings import Settings
from owlin_bot.modules.publishing.setup import setup


@pytest.mark.asyncio
async def test_setup_builds_service_registers_cog_and_stores_it():
    settings = Settings(
        discord_token="test-token",
        restricted_channel_id=7,
        publish_command_channel_id=10,
    )
    bot = SimpleNamespace(
        settings=settings,
        discord_client=SimpleNamespace(),
        services=Services(),
        add_cog=AsyncMock(),
    )

    await setup(bot)

    bot.add_cog.assert_awaited_once()
    assert bot.services.publishing is not None
