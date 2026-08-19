"""Create and configure the single Discord bot instance."""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from owlin_bot.constants import COMMAND_PREFIX
from owlin_bot.handlers.moderation_handler import ModerationHandler
from owlin_bot.integrations.discord_client import DiscordClient
from owlin_bot.services.moderation_service import ModerationService
from owlin_bot.settings import Settings

logger = logging.getLogger(__name__)


def create_bot(settings: Settings) -> commands.Bot:
    """Create the single Discord bot and register feature handlers."""
    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=COMMAND_PREFIX,
        intents=intents,
        help_command=None,
    )

    discord_client = DiscordClient(bot)
    moderation_service = ModerationService(settings, discord_client)
    moderation_handler = ModerationHandler(moderation_service)
    bot.add_listener(moderation_handler.handle_message, "on_message")

    async def handle_ready() -> None:
        """Log successful Discord connection."""
        logger.info("Logged in as %s (%s)", bot.user, bot.user.id if bot.user else "unknown")

    bot.add_listener(handle_ready, "on_ready")

    return bot
