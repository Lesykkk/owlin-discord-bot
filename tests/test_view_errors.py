from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from owlin_bot.app.error_handling.manager import ErrorReportingManager
from owlin_bot.app.error_handling.view_errors import SafeModal, SafeView


def make_interaction(*, response_done: bool = False) -> SimpleNamespace:
    response = SimpleNamespace(is_done=lambda: response_done, send_message=AsyncMock())
    followup = SimpleNamespace(send=AsyncMock())
    return SimpleNamespace(response=response, followup=followup, user=SimpleNamespace(id=99))


@pytest.mark.asyncio
async def test_safe_view_answers_interaction_on_error():
    interaction = make_interaction()
    view = SafeView(ErrorReportingManager())
    item = SimpleNamespace()

    await view.on_error(interaction, RuntimeError("boom"), item)

    interaction.response.send_message.assert_awaited_once_with(
        "Something went wrong. This has been logged.", ephemeral=True
    )


@pytest.mark.asyncio
async def test_safe_modal_answers_interaction_on_error():
    interaction = make_interaction(response_done=True)
    modal = SafeModal(ErrorReportingManager(), title="Buy account")

    await modal.on_error(interaction, RuntimeError("boom"))

    interaction.followup.send.assert_awaited_once_with(
        "Something went wrong. This has been logged.", ephemeral=True
    )
