"""Centralized handling for command and Discord event errors."""

from __future__ import annotations

import logging

from discord.ext import commands

from owlin_bot.integrations.discord_client import DiscordClient
from owlin_bot.shared.errors import RequestError

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Send expected command errors and log all unexpected failures."""

    def __init__(self, discord_client: DiscordClient) -> None:
        self._discord_client = discord_client

    async def handle_command_error(
        self,
        context: commands.Context[commands.Bot],
        error: commands.CommandError,
    ) -> None:
        """Handle errors raised while processing a command."""
        if isinstance(error, commands.CommandNotFound):
            return

        original_error = self._unwrap_command_error(error)
        message = self._get_user_message(original_error)
        if message is not None:
            await self._discord_client.send_message(context.channel.id, message)
            return

        logger.error(
            "Unhandled command error: %s",
            original_error,
            exc_info=(
                type(original_error),
                original_error,
                original_error.__traceback__,
            ),
        )

    async def handle_event_error(self, event_name: str) -> None:
        """Log an unhandled Discord event error."""
        logger.exception("Unhandled Discord event: %s", event_name)

    @staticmethod
    def _unwrap_command_error(error: commands.CommandError) -> Exception:
        """Return the original exception raised by a command handler."""
        if isinstance(error, commands.CommandInvokeError):
            return error.original
        return error

    @staticmethod
    def _get_user_message(error: Exception) -> str | None:
        """Return a response for expected command errors."""
        if isinstance(error, RequestError):
            return str(error)
        if isinstance(error, commands.NoPrivateMessage):
            return "This command can only be used in a server."
        if isinstance(error, commands.CheckFailure):
            return "You do not have permission to use this command."
        if isinstance(error, commands.MissingRequiredArgument):
            return "This command is missing required arguments."
        if isinstance(error, commands.BadArgument):
            return "Invalid command arguments."
        return None
