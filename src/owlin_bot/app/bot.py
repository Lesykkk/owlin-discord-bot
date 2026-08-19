"""Create and configure the single Discord bot instance."""

from __future__ import annotations

import discord
from discord.ext import commands

from owlin_bot.app.constants import COMMAND_PREFIX
from owlin_bot.app.registry import register
from owlin_bot.app.settings import Settings
from owlin_bot.integrations.discord_client import DiscordClient


def create_bot(settings: Settings) -> commands.Bot:
    """Create the single Discord bot and register all modules."""
    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True

    bot = commands.Bot(
        command_prefix=COMMAND_PREFIX,
        intents=intents,
        help_command=None,
    )
    register(bot, settings, DiscordClient(bot))
    return bot
