"""Translate discord.ext.commands errors into log entries and user messages."""

from __future__ import annotations

from discord.ext import commands

from owlin_bot.app.error_handling.manager import ErrorReportingManager
from owlin_bot.app.error_handling.surface_handler import ErrorSurfaceHandler
from owlin_bot.integrations.discord_client import DiscordClient


class CommandErrorHandler(ErrorSurfaceHandler):
    """Report and respond to errors raised while processing a text command."""

    def __init__(self, discord_client: DiscordClient, manager: ErrorReportingManager) -> None:
        super().__init__(manager)
        self._discord_client = discord_client

    async def handle(
        self,
        context: commands.Context[commands.Bot],
        error: commands.CommandError,
    ) -> None:
        """Handle an error raised while processing a text command."""
        if isinstance(error, commands.CommandNotFound):
            # Raised when the user typed a command name that does not exist.
            return

        original = self._unwrap(error)
        message, expected = self._classify(original)
        self._manager.report(
            surface="command",
            error=original,
            expected=expected,
            command=context.command.qualified_name if context.command else context.invoked_with,
            user=context.author.id,
            guild=context.guild.id if context.guild else "dm",
        )

        await self._discord_client.send_message(context.channel.id, message)

    def _known_error_message(self, error: BaseException) -> str | None:
        """Map well-known discord.ext.commands exceptions to a friendly message."""
        if isinstance(error, commands.NoPrivateMessage):
            # Raised when a guild-only command is used in a DM with the bot.
            return "This command can only be used in a server."
        if isinstance(error, commands.CommandOnCooldown):
            # Raised when the user re-triggers a rate-limited command too soon.
            return f"This command is on cooldown. Try again in {error.retry_after:.1f}s."
        if isinstance(error, commands.CheckFailure):
            # Raised by any failed @commands.check, e.g. missing admin/owner rights
            # or being called outside the one allowed channel.
            return "You do not have permission to use this command."
        if isinstance(error, commands.MissingRequiredArgument):
            # Raised when the user did not pass all the arguments the command needs.
            return "This command is missing required arguments."
        if isinstance(error, commands.BadArgument):
            # Raised when an argument was passed but could not be converted,
            # e.g. a channel mention that does not resolve to a real channel.
            return "Invalid command arguments."
        return None
