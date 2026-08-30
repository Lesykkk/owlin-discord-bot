"""Central place every error surface reports through."""

from __future__ import annotations

import logging

from owlin_bot.shared.errors import UserFacingError

logger = logging.getLogger(__name__)


class ErrorReportingManager:
    """Log every caught exception with context and decide the user-facing message."""

    def report(self, *, surface: str, error: BaseException, **context: object) -> None:
        """Log an exception from any error surface with structured context."""
        details = " ".join(f"{key}={value}" for key, value in context.items())
        logger.error("%s error: %s error=%s", surface, details, error, exc_info=error)

    @staticmethod
    def to_user_message(error: BaseException) -> str:
        """Return the text that is safe to show a user for a caught exception."""
        if isinstance(error, UserFacingError):
            return str(error)
        return "Something went wrong. This has been logged."
