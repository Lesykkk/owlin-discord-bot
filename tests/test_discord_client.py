from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from owlin_bot.integrations.discord_client import DiscordClient


@pytest.mark.asyncio
async def test_send_embed_preserves_content_and_color():
    channel = MagicMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    bot = SimpleNamespace(get_channel=lambda channel_id: channel, fetch_channel=AsyncMock())

    await DiscordClient(bot).send_embed(42, "**Hello**", color=0x7A00FF)

    embed = channel.send.await_args.kwargs["embed"]
    assert embed.description == "**Hello**"
    assert embed.colour.value == 0x7A00FF


@pytest.mark.asyncio
async def test_send_embed_returns_discord_error():
    channel = MagicMock(spec=discord.TextChannel)
    channel.send = AsyncMock(side_effect=discord.DiscordException("send failed"))
    bot = SimpleNamespace(get_channel=lambda channel_id: channel, fetch_channel=AsyncMock())

    with pytest.raises(discord.DiscordException, match="send failed"):
        await DiscordClient(bot).send_embed(42, "Hello", color=0x7A00FF)

@pytest.mark.asyncio
async def test_send_message_uses_cached_channel():
    channel = MagicMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    bot = SimpleNamespace(get_channel=lambda channel_id: channel, fetch_channel=AsyncMock())

    await DiscordClient(bot).send_message(42, "Error")

    channel.send.assert_awaited_once_with("Error")
    bot.fetch_channel.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_message_uses_cached_channel():
    message = SimpleNamespace(delete=AsyncMock())
    channel = MagicMock(spec=discord.TextChannel)
    channel.fetch_message = AsyncMock(return_value=message)
    bot = SimpleNamespace(get_channel=lambda channel_id: channel, fetch_channel=AsyncMock())

    await DiscordClient(bot).delete_message(42, 99)

    channel.fetch_message.assert_awaited_once_with(99)
    message.delete.assert_awaited_once_with()
    bot.fetch_channel.assert_not_awaited()


@pytest.mark.asyncio
async def test_ban_member_uses_cached_member():
    member = SimpleNamespace(ban=AsyncMock())
    guild = SimpleNamespace(get_member=lambda member_id: member, fetch_member=AsyncMock())
    bot = SimpleNamespace(get_guild=lambda guild_id: guild, fetch_guild=AsyncMock())

    await DiscordClient(bot).ban_member(
        42,
        99,
        reason="test",
        delete_message_seconds=300,
    )

    member.ban.assert_awaited_once_with(reason="test", delete_message_seconds=300)
    guild.fetch_member.assert_not_awaited()


@pytest.mark.asyncio
async def test_ban_member_returns_discord_error():
    member = SimpleNamespace(
        ban=AsyncMock(side_effect=discord.DiscordException("ban failed"))
    )
    guild = SimpleNamespace(get_member=lambda member_id: member, fetch_member=AsyncMock())
    bot = SimpleNamespace(get_guild=lambda guild_id: guild, fetch_guild=AsyncMock())

    with pytest.raises(discord.DiscordException, match="ban failed"):
        await DiscordClient(bot).ban_member(
            42,
            99,
            reason="test",
            delete_message_seconds=300,
        )


@pytest.mark.asyncio
async def test_unban_member_uses_guild_unban():
    guild = SimpleNamespace(unban=AsyncMock())
    bot = SimpleNamespace(get_guild=lambda guild_id: guild, fetch_guild=AsyncMock())

    await DiscordClient(bot).unban_member(42, 99, reason="test")

    unbanned_user = guild.unban.await_args.args[0]
    assert unbanned_user.id == 99
    guild.unban.assert_awaited_once_with(unbanned_user, reason="test")
    bot.fetch_guild.assert_not_awaited()


@pytest.mark.asyncio
async def test_unban_member_returns_discord_error():
    guild = SimpleNamespace(
        unban=AsyncMock(side_effect=discord.DiscordException("unban failed"))
    )
    bot = SimpleNamespace(get_guild=lambda guild_id: guild, fetch_guild=AsyncMock())

    with pytest.raises(discord.DiscordException, match="unban failed"):
        await DiscordClient(bot).unban_member(42, 99, reason="test")
