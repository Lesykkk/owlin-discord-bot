from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from discord import app_commands

from owlin_bot.app.error_handling.app_command_errors import AppCommandErrorHandler
from owlin_bot.app.error_handling.manager import ErrorReportingManager
from owlin_bot.shared.errors import RequestError


def make_interaction(*, response_done: bool = False) -> SimpleNamespace:
    response = SimpleNamespace(is_done=lambda: response_done, send_message=AsyncMock())
    followup = SimpleNamespace(send=AsyncMock())
    return SimpleNamespace(
        response=response,
        followup=followup,
        user=SimpleNamespace(id=99),
        guild_id=42,
        command=SimpleNamespace(name="market", qualified_name="market"),
    )


@pytest.mark.asyncio
async def test_sends_initial_response_when_not_yet_acknowledged():
    interaction = make_interaction(response_done=False)
    handler = AppCommandErrorHandler(ErrorReportingManager())

    await handler.handle(interaction, RequestError("No accounts available."))

    interaction.response.send_message.assert_awaited_once_with(
        "No accounts available.", ephemeral=True
    )
    interaction.followup.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_sends_followup_when_already_acknowledged():
    interaction = make_interaction(response_done=True)
    handler = AppCommandErrorHandler(ErrorReportingManager())

    await handler.handle(interaction, RequestError("No accounts available."))

    interaction.followup.send.assert_awaited_once_with(
        "No accounts available.", ephemeral=True
    )
    interaction.response.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_unwraps_command_invoke_error():
    interaction = make_interaction()
    handler = AppCommandErrorHandler(ErrorReportingManager())
    error = app_commands.CommandInvokeError(interaction.command, RequestError("bad input"))

    await handler.handle(interaction, error)

    interaction.response.send_message.assert_awaited_once_with("bad input", ephemeral=True)


@pytest.mark.asyncio
async def test_cooldown_error_shows_retry_after():
    interaction = make_interaction()
    handler = AppCommandErrorHandler(ErrorReportingManager())
    error = app_commands.CommandOnCooldown(SimpleNamespace(rate=1, per=30.0), 12.3)

    await handler.handle(interaction, error)

    interaction.response.send_message.assert_awaited_once_with(
        "This command is on cooldown. Try again in 12.3s.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_unexpected_error_gets_generic_message():
    interaction = make_interaction()
    handler = AppCommandErrorHandler(ErrorReportingManager())

    await handler.handle(interaction, RuntimeError("boom"))

    interaction.response.send_message.assert_awaited_once_with(
        "Something went wrong. This has been logged.", ephemeral=True
    )
