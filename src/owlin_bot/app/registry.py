"""Connect application modules to the Discord bot."""

from __future__ import annotations

import logging
from functools import partial
from typing import Any

from discord.ext import commands

from owlin_bot.app.error_handler import ErrorHandler
from owlin_bot.app.settings import Settings
from owlin_bot.integrations.discord_client import DiscordClient
from owlin_bot.modules.moderation.events import register as register_moderation_events
from owlin_bot.modules.moderation.service import ModerationService
from owlin_bot.modules.publishing.commands import register as register_publishing_commands
from owlin_bot.modules.publishing.service import PublishingService

logger = logging.getLogger(__name__)


def register(
    bot: commands.Bot,
    settings: Settings,
    discord_client: DiscordClient,
) -> None:
    """Register every application module and global Discord callback."""
    error_handler = ErrorHandler(discord_client)
    register_moderation_events(
        bot,
        ModerationService(settings, discord_client),
    )
    register_publishing_commands(
        bot,
        settings,
        PublishingService(settings, discord_client),
    )
    bot.add_listener(error_handler.handle_command_error, "on_command_error")
    _register_event_error_handler(bot, error_handler)
    bot.add_listener(partial(_handle_ready, bot), "on_ready")


def _register_event_error_handler(
    bot: commands.Bot,
    error_handler: ErrorHandler,
) -> None:
    """Register one global handler for every unhandled Discord event error."""

    async def on_error(
        event_name: str,
        /,
        *_args: Any,
        **_kwargs: Any,
    ) -> None:
        await error_handler.handle_event_error(event_name)

    bot.event(on_error)


async def _handle_ready(bot: commands.Bot) -> None:
    """Log successful Discord connection."""
    logger.info("Logged in as %s (%s)", bot.user, bot.user.id if bot.user else "unknown")
