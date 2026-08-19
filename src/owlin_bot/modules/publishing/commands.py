"""Discord command adapter for publishing."""

from __future__ import annotations

import discord
from discord.ext import commands

from owlin_bot.app.authorization import (
    is_administrator_or_owner,
    is_guild_context,
    is_in_channel,
)
from owlin_bot.app.settings import Settings
from owlin_bot.modules.publishing.models import PublishRequest
from owlin_bot.modules.publishing.service import PublishingService


class PublishingCommands:
    """Convert publishing commands into publishing use-case input."""

    def __init__(self, service: PublishingService) -> None:
        self._service = service

    async def publish(
        self,
        context: commands.Context[commands.Bot],
        target_channel: discord.TextChannel,
        *,
        content: str,
    ) -> None:
        """Handle !publish without deleting the source message."""
        if context.guild is None:
            return

        await self._service.publish(
            PublishRequest(
                source_guild_id=context.guild.id,
                source_channel_id=context.channel.id,
                target_guild_id=target_channel.guild.id,
                target_channel_id=target_channel.id,
                content=content,
            )
        )


def register(
    bot: commands.Bot,
    settings: Settings,
    service: PublishingService,
) -> None:
    """Register publishing commands and their authorization rules."""
    publishing_commands = PublishingCommands(service)
    bot.command(
        name="publish",
        checks=[
            is_guild_context,
            is_administrator_or_owner,
            is_in_channel(settings.publish_command_channel_id),
        ],
    )(publishing_commands.publish)
