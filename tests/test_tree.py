from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from owlin_bot.app.tree import OwlinCommandTree


@pytest.mark.asyncio
async def test_on_error_does_nothing_without_a_handler():
    tree = OwlinCommandTree.__new__(OwlinCommandTree)

    await tree.on_error(SimpleNamespace(), RuntimeError("boom"))  # must not raise


@pytest.mark.asyncio
async def test_on_error_delegates_to_the_assigned_handler():
    tree = OwlinCommandTree.__new__(OwlinCommandTree)
    tree.handler = SimpleNamespace(handle=AsyncMock())
    interaction = SimpleNamespace()
    error = RuntimeError("boom")

    await tree.on_error(interaction, error)

    tree.handler.handle.assert_awaited_once_with(interaction, error)
