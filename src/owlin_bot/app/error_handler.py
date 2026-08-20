"""Centralized handling for command and Discord event errors."""

from __future__ import annotations

import logging
import sys

from discord.ext import commands

from owlin_bot.integrations.discord_client import DiscordClient
from owlin_bot.shared.errors import RequestError

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Send expected errors and log unexpected failures."""

    def __init__(self, discord_client: DiscordClient) -> None:
        self._discord_client = discord_client

    async def handle_command_error(
        self,
        context: commands.Context[commands.Bot],
        error: commands.CommandError,
    ) -> None:
        """Handle errors raised while processing a command."""
        if isinstance(error, commands.CommandNotFound):
            self._log_command_error(context, error)
            return

        original_error = self._unwrap_command_error(error)
        self._log_command_error(context, original_error)
        message = self._get_user_message(original_error)
        if message is not None:
            await self._discord_client.send_message(context.channel.id, message)

    async def handle_event_error(self, _event_name: str) -> None:
        """Log an unexpected Discord event error."""
        logger.error(
            "Event error: event=%s error=%s",
            _event_name,
            sys.exc_info()[1],
        )

    @staticmethod
    def _log_command_error(
        context: commands.Context[commands.Bot],
        error: Exception,
    ) -> None:
        """Log one command error with its Discord context."""
        logger.error(
            "Command error: command=%s user=%s guild=%s error=%s",
            context.command.qualified_name
            if context.command
            else context.invoked_with or "unknown",
            context.author.id,
            context.guild.id if context.guild else "dm",
            error,
        )

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
