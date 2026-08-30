"""Create and configure the single Discord bot instance."""

from __future__ import annotations

from typing import cast

import discord
from discord.ext import commands

from owlin_bot.app.composition import configure_error_handling, configure_lifecycle
from owlin_bot.app.constants import COMMAND_PREFIX
from owlin_bot.app.services import Services
from owlin_bot.app.settings import Settings
from owlin_bot.app.tree import OwlinCommandTree
from owlin_bot.integrations.discord_client import DiscordClient

EXTENSIONS: tuple[str, ...] = (
    "owlin_bot.modules.moderation.setup",
    "owlin_bot.modules.publishing.setup",
)


class OwlinBot(commands.Bot):
    """Discord bot that loads each module as its own extension.

    Adding a module means appending one path to EXTENSIONS below.
    """

    settings: Settings
    discord_client: DiscordClient
    services: Services

    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None,
            tree_cls=OwlinCommandTree,
        )
        self.settings = settings

    async def setup_hook(self) -> None:
        """Wire shared infrastructure, then let each module load itself."""
        self.discord_client = DiscordClient(self)
        self.services = Services()

        for extension in EXTENSIONS:
            await self.load_extension(extension)

        # discord.py types Bot.tree generically as CommandTree[OwlinBot]; we know
        # it is actually an OwlinCommandTree because we passed tree_cls= above.
        tree = cast(OwlinCommandTree, self.tree)
        configure_error_handling(self, tree, self.discord_client)
        configure_lifecycle(self)


def create_bot(settings: Settings) -> commands.Bot:
    """Create the single Discord bot."""
    return OwlinBot(settings)
