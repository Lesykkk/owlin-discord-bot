"""Discord API operations used by application services."""

from __future__ import annotations

import discord


class DiscordClient:
    """Performs Discord API operations for application services."""

    def __init__(self, bot: discord.Client) -> None:
        self._bot = bot

    async def send_embed(
        self,
        channel_id: int,
        content: str,
        *,
        color: int,
    ) -> None:
        """Send content as a formatted embed to a text channel or thread."""
        channel = self._bot.get_channel(channel_id)
        if channel is None:
            channel = await self._bot.fetch_channel(channel_id)

        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            raise ValueError(f"Channel {channel_id} cannot receive embeds")

        embed = discord.Embed(
            description=content,
            colour=discord.Colour(color),
        )
        await channel.send(embed=embed)

    async def send_message(self, channel_id: int, content: str) -> None:
        """Send a plain text message to a Discord messageable channel."""
        channel = self._bot.get_channel(channel_id)
        if channel is None:
            channel = await self._bot.fetch_channel(channel_id)

        if not isinstance(channel, discord.abc.Messageable):
            raise ValueError(f"Channel {channel_id} cannot receive messages")

        await channel.send(content)

    async def delete_message(self, channel_id: int, message_id: int) -> None:
        """Delete one message from a Discord text channel or thread."""
        channel = self._bot.get_channel(channel_id)
        if channel is None:
            channel = await self._bot.fetch_channel(channel_id)

        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            raise ValueError(f"Channel {channel_id} cannot contain messages")

        message = await channel.fetch_message(message_id)
        await message.delete()

    async def ban_member(
        self,
        guild_id: int,
        member_id: int,
        *,
        reason: str,
        delete_message_seconds: int,
    ) -> None:
        """Ban a guild member and delete their recent guild messages."""
        guild = await self._get_guild(guild_id)

        member = guild.get_member(member_id)
        if member is None:
            member = await guild.fetch_member(member_id)

        await member.ban(
            reason=reason,
            delete_message_seconds=delete_message_seconds,
        )

    async def unban_member(
        self,
        guild_id: int,
        member_id: int,
        *,
        reason: str,
    ) -> None:
        """Unban a member from a guild."""
        guild = await self._get_guild(guild_id)
        await guild.unban(discord.Object(id=member_id), reason=reason)

    async def _get_guild(self, guild_id: int) -> discord.Guild:
        """Return a cached guild or fetch it from Discord."""
        guild = self._bot.get_guild(guild_id)
        if guild is None:
            guild = await self._bot.fetch_guild(guild_id)
        return guild
