"""Discord API operations used by application services."""

from __future__ import annotations

import discord

from owlin_bot.models.moderation import ActionResult


class DiscordClient:
    """Performs Discord API operations for application services."""

    def __init__(self, bot: discord.Client) -> None:
        self._bot = bot

    async def ban_member(
        self,
        guild_id: int,
        member_id: int,
        *,
        reason: str,
        delete_message_seconds: int,
    ) -> ActionResult:
        """Ban a guild member and delete their recent guild messages."""
        try:
            guild = await self._get_guild(guild_id)

            member = guild.get_member(member_id)
            if member is None:
                member = await guild.fetch_member(member_id)

            await member.ban(
                reason=reason,
                delete_message_seconds=delete_message_seconds,
            )
        except discord.DiscordException as exc:
            return ActionResult(
                succeeded=False,
                error=f"{type(exc).__name__}: {exc}",
            )
        return ActionResult(succeeded=True)

    async def _get_guild(self, guild_id: int) -> discord.Guild:
        """Return a cached guild or fetch it from Discord."""
        guild = self._bot.get_guild(guild_id)
        if guild is None:
            guild = await self._bot.fetch_guild(guild_id)
        return guild
