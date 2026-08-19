"""Translate Discord message events into moderation service calls."""

from __future__ import annotations

import discord

from owlin_bot.models.moderation import MessageEvent
from owlin_bot.services.moderation_service import ModerationService


class ModerationHandler:
    """Converts Discord messages into moderation service calls."""

    def __init__(self, service: ModerationService) -> None:
        self._service = service

    async def handle_message(self, message: discord.Message) -> None:
        """Convert one Discord message into a moderation event."""
        member = message.author if isinstance(message.author, discord.Member) else None
        guild = message.guild

        event = MessageEvent(
            guild_id=guild.id if guild else None,
            channel_id=message.channel.id,
            author_id=message.author.id,
            author_is_bot=message.author.bot,
            author_is_server_owner=bool(member and guild and member.id == guild.owner_id),
            author_is_administrator=bool(member and member.guild_permissions.administrator),
            created_at=message.created_at,
        )
        await self._service.handle_message(event)
