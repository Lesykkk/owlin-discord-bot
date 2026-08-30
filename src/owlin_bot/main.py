"""Application entry point."""

from __future__ import annotations

import logging

from owlin_bot.app.bot import create_bot
from owlin_bot.app.context import FlowIdLogFilter
from owlin_bot.app.settings import Settings


def main() -> None:
    """Load settings and start the Discord bot."""
    settings = Settings.from_environment()
    _configure_logging()

    bot = create_bot(settings)
    bot.run(settings.discord_token, log_handler=None)


def _configure_logging() -> None:
    """Attach a correlation-id-aware formatter to the root logger."""
    handler = logging.StreamHandler()
    handler.addFilter(FlowIdLogFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(flow_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.basicConfig(level=logging.INFO, handlers=[handler])


if __name__ == "__main__":
    main()
