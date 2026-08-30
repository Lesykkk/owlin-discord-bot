"""Discord extension entrypoint for the moderation module."""

from __future__ import annotations

from owlin_bot.app.bot import OwlinBot
from owlin_bot.modules.moderation.events import register
from owlin_bot.modules.moderation.service import ModerationService


async def setup(bot: OwlinBot) -> None:
    """Build the moderation service and register its Discord listeners."""
    service = ModerationService(bot.settings, bot.discord_client)
    register(bot, service)
    bot.services.moderation = service
