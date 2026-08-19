"""Create and configure the single Discord bot instance."""

from __future__ import annotations

import discord
from discord.ext import commands

from owlin_bot.app.constants import COMMAND_PREFIX
from owlin_bot.app.registry import register
from owlin_bot.app.settings import Settings
from owlin_bot.integrations.discord_client import DiscordClient


class OwlinBot(commands.Bot):
    """Discord bot that registers modules during startup."""

    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None,
        )
        self._settings = settings

    async def setup_hook(self) -> None:
        """Register modules before connecting to Discord."""
        await register(self, self._settings, DiscordClient(self))


def create_bot(settings: Settings) -> commands.Bot:
    """Create the single Discord bot."""
    return OwlinBot(settings)
