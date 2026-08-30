from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest

from owlin_bot.app.error_handling.interaction_reply import respond_to_interaction


def make_interaction(*, response_done: bool, send_error: Exception | None = None) -> SimpleNamespace:
    response = SimpleNamespace(
        is_done=lambda: response_done,
        send_message=AsyncMock(side_effect=send_error),
    )
    followup = SimpleNamespace(send=AsyncMock(side_effect=send_error))
    return SimpleNamespace(response=response, followup=followup)


@pytest.mark.asyncio
async def test_sends_initial_response_when_not_acknowledged():
    interaction = make_interaction(response_done=False)

    await respond_to_interaction(interaction, "hello")

    interaction.response.send_message.assert_awaited_once_with("hello", ephemeral=True)


@pytest.mark.asyncio
async def test_sends_followup_when_already_acknowledged():
    interaction = make_interaction(response_done=True)

    await respond_to_interaction(interaction, "hello")

    interaction.followup.send.assert_awaited_once_with("hello", ephemeral=True)


@pytest.mark.asyncio
async def test_swallows_http_exception_when_interaction_token_is_dead():
    dead_token_error = discord.HTTPException(
        SimpleNamespace(status=404, reason="Not Found"), "Unknown interaction"
    )
    interaction = make_interaction(response_done=True, send_error=dead_token_error)

    await respond_to_interaction(interaction, "hello")  # must not raise
