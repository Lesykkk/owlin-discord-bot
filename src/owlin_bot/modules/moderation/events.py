"""Discord event adapter for moderation."""

from __future__ import annotations

import discord
from discord.ext import commands

from owlin_bot.modules.moderation.models import MessageEvent
from owlin_bot.modules.moderation.service import ModerationService


class ModerationEvents:
    """Convert Discord events into moderation use-case input."""

    def __init__(self, service: ModerationService) -> None:
        self._service = service

    async def on_message(self, message: discord.Message) -> None:
        """Pass a received Discord message to moderation."""
        member = message.author if isinstance(message.author, discord.Member) else None
        guild = message.guild
        event = MessageEvent(
            message_id=message.id,
            guild_id=guild.id if guild else None,
            channel_id=message.channel.id,
            author_id=message.author.id,
            author_is_bot=message.author.bot,
            author_is_server_owner=bool(member and guild and member.id == guild.owner_id),
            author_is_administrator=bool(member and member.guild_permissions.administrator),
            created_at=message.created_at,
        )
        await self._service.handle_message(event)


def register(
    bot: commands.Bot,
    service: ModerationService,
) -> None:
    """Register moderation Discord event listeners."""
    events = ModerationEvents(service)
    bot.add_listener(events.on_message, "on_message")
