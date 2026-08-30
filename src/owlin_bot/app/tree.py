"""Command tree that lets slash-command error handling be attached after construction."""

from __future__ import annotations

import discord
from discord import app_commands

from owlin_bot.app.error_handling.app_command_errors import AppCommandErrorHandler


class OwlinCommandTree(app_commands.CommandTree):
    """A CommandTree whose slash-command errors are delegated to an assignable handler.

    discord.py builds this tree inside Bot.__init__, before the rest of the app
    is wired up, so the handler cannot be passed to the constructor. `handler`
    is assigned once, from the composition root, right after the bot is created.
    """

    handler: AppCommandErrorHandler | None = None

    async def on_error(  # pylint: disable=arguments-differ
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Delegate every slash-command error to the assigned handler, if any."""
        if self.handler is not None:
            await self.handler.handle(interaction, error)
