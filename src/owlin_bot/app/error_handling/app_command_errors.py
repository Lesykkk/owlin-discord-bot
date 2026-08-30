"""Translate discord.app_commands errors into log entries and user messages."""

from __future__ import annotations

import discord
from discord import app_commands

from owlin_bot.app.error_handling.interaction_reply import respond_to_interaction
from owlin_bot.app.error_handling.surface_handler import ErrorSurfaceHandler


class AppCommandErrorHandler(ErrorSurfaceHandler):
    """Report and respond to errors raised while processing a slash command."""

    async def handle(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Handle an error raised while processing a slash command or autocomplete."""
        original = self._unwrap(error)
        message, expected = self._classify(original)
        self._manager.report(
            surface="app_command",
            error=original,
            expected=expected,
            command=interaction.command.qualified_name if interaction.command else "unknown",
            user=interaction.user.id,
            guild=interaction.guild_id or "dm",
        )

        await respond_to_interaction(interaction, message)

    def _known_error_message(self, error: BaseException) -> str | None:
        """Map well-known discord.app_commands exceptions to a friendly message."""
        if isinstance(error, app_commands.CommandOnCooldown):
            # Raised when the user re-triggers a rate-limited slash command too soon.
            # Must be checked before CheckFailure below, since it is a subclass of it.
            return f"This command is on cooldown. Try again in {error.retry_after:.1f}s."
        if isinstance(error, app_commands.CheckFailure):
            # Raised by a failed slash-command check, e.g. missing permissions.
            return str(error) or "You do not have permission to use this command."
        return None
