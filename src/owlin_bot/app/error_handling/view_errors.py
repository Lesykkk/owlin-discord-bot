"""Base classes for interactive components with consistent error handling."""

from __future__ import annotations

from typing import Any

import discord

from owlin_bot.app.error_handling.interaction_reply import respond_to_interaction
from owlin_bot.app.error_handling.manager import ErrorReportingManager


class SafeView(discord.ui.View):
    """A View that reports errors and always answers the interaction."""

    def __init__(self, manager: ErrorReportingManager, *, timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)
        self._manager = manager

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any],
        /,
    ) -> None:
        """Log the error and tell the user something went wrong."""
        self._manager.report(
            surface="view",
            error=error,
            expected=self._manager.is_expected(error),
            item=item.__class__.__name__,
            user=interaction.user.id,
        )
        await respond_to_interaction(interaction, self._manager.to_user_message(error))


class SafeModal(discord.ui.Modal):
    """A Modal that reports errors and always answers the interaction."""

    def __init__(self, manager: ErrorReportingManager, *, title: str) -> None:
        super().__init__(title=title)
        self._manager = manager

    async def on_error(  # type: ignore[override]
        self, interaction: discord.Interaction, error: Exception, /
    ) -> None:
        """Log the error and tell the user something went wrong."""
        self._manager.report(
            surface="modal",
            error=error,
            expected=self._manager.is_expected(error),
            user=interaction.user.id,
        )
        await respond_to_interaction(interaction, self._manager.to_user_message(error))
