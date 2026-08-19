from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from owlin_bot.integrations.discord_client import DiscordClient


@pytest.mark.asyncio
async def test_delete_message_uses_cached_channel():
    message = SimpleNamespace(delete=AsyncMock())
    channel = MagicMock(spec=discord.TextChannel)
    channel.fetch_message = AsyncMock(return_value=message)
    bot = SimpleNamespace(get_channel=lambda channel_id: channel, fetch_channel=AsyncMock())

    result = await DiscordClient(bot).delete_message(42, 99)

    assert result.succeeded is True
    channel.fetch_message.assert_awaited_once_with(99)
    message.delete.assert_awaited_once_with()
    bot.fetch_channel.assert_not_awaited()


@pytest.mark.asyncio
async def test_ban_member_uses_cached_member():
    member = SimpleNamespace(ban=AsyncMock())
    guild = SimpleNamespace(get_member=lambda member_id: member, fetch_member=AsyncMock())
    bot = SimpleNamespace(get_guild=lambda guild_id: guild, fetch_guild=AsyncMock())

    result = await DiscordClient(bot).ban_member(
        42,
        99,
        reason="test",
        delete_message_seconds=300,
    )

    assert result.succeeded is True
    member.ban.assert_awaited_once_with(reason="test", delete_message_seconds=300)
    guild.fetch_member.assert_not_awaited()


@pytest.mark.asyncio
async def test_ban_member_returns_discord_error():
    member = SimpleNamespace(
        ban=AsyncMock(side_effect=discord.DiscordException("ban failed"))
    )
    guild = SimpleNamespace(get_member=lambda member_id: member, fetch_member=AsyncMock())
    bot = SimpleNamespace(get_guild=lambda guild_id: guild, fetch_guild=AsyncMock())

    result = await DiscordClient(bot).ban_member(
        42,
        99,
        reason="test",
        delete_message_seconds=300,
    )

    assert result.succeeded is False
    assert result.error == "DiscordException: ban failed"
