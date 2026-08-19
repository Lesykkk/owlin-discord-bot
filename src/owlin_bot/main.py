"""Application entry point."""

from __future__ import annotations

import logging

from owlin_bot.app.bot import create_bot
from owlin_bot.app.settings import Settings


def main() -> None:
    """Load settings and start the Discord bot."""
    settings = Settings.from_environment()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bot = create_bot(settings)
    bot.run(settings.discord_token, log_handler=None)
