"""Cross-cutting bot wiring that is not owned by any single module.

Each module registers itself as a Discord extension (see EXTENSIONS in
app/bot.py); this file only wires infrastructure that spans every module:
error reporting and the bot's own lifecycle hooks.
"""

from __future__ import annotations

import logging
import sys
from functools import partial
from typing import Any

from discord.ext import commands

from owlin_bot.app.context import bind_flow_id
from owlin_bot.app.error_handling import (
    AppCommandErrorHandler,
    CommandErrorHandler,
    ErrorReportingManager,
)
from owlin_bot.app.tree import OwlinCommandTree
from owlin_bot.integrations.discord_client import DiscordClient

logger = logging.getLogger(__name__)


def configure_error_handling(
    bot: commands.Bot,
    tree: OwlinCommandTree,
    discord_client: DiscordClient,
) -> None:
    """Wire every error surface into one shared error-reporting manager."""
    manager = ErrorReportingManager()

    command_handler = CommandErrorHandler(discord_client, manager)
    bot.add_listener(command_handler.handle, "on_command_error")

    tree.handler = AppCommandErrorHandler(manager)

    _configure_raw_event_error_handler(bot, manager)


def _configure_raw_event_error_handler(bot: commands.Bot, manager: ErrorReportingManager) -> None:
    """Report every unhandled exception raised inside a raw event listener."""

    async def on_error(event_name: str, /, *_args: Any, **_kwargs: Any) -> None:
        error = sys.exc_info()[1] or RuntimeError("unknown event error")
        manager.report(surface=f"event:{event_name}", error=error)

    bot.event(on_error)


def configure_lifecycle(bot: commands.Bot) -> None:
    """Register hooks about the bot's own lifecycle, not any single module."""
    bot.before_invoke(_bind_command_flow_id)
    bot.add_listener(partial(_handle_ready, bot), "on_ready")


async def _bind_command_flow_id(context: commands.Context[commands.Bot]) -> None:
    """Bind the invoking message id as the correlation id for a text command."""
    bind_flow_id(str(context.message.id))


async def _handle_ready(bot: commands.Bot) -> None:
    """Log a successful Discord connection."""
    logger.info(
        "Ready: user=%s id=%s",
        bot.user,
        bot.user.id if bot.user else "unknown",
    )
