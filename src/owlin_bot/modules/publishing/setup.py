"""Discord extension entrypoint for the publishing module."""

from __future__ import annotations

from owlin_bot.app.bot import OwlinBot
from owlin_bot.modules.publishing.commands import register
from owlin_bot.modules.publishing.service import PublishingService


async def setup(bot: OwlinBot) -> None:
    """Build the publishing service and register its commands."""
    service = PublishingService(bot.settings, bot.discord_client)
    await register(bot, bot.settings, service)
    bot.services.publishing = service
