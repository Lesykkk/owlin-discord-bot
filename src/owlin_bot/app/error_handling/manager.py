"""Central place every error surface reports through."""

from __future__ import annotations

import logging

from owlin_bot.shared.errors import UserFacingError

logger = logging.getLogger(__name__)


class ErrorReportingManager:
    """Log every caught exception with context and decide the user-facing message."""

    def report(
        self, *, surface: str, error: BaseException, expected: bool, **context: object
    ) -> None:
        """Log an exception from any error surface with structured context.

        `expected` marks a routine, already-translated mistake that does not
        need a full traceback in the logs every time a user makes a typo.
        """
        details = " ".join(f"{key}={value}" for key, value in context.items())
        if expected:
            logger.info("%s error: %s error=%s", surface, details, error)
        else:
            logger.error("%s error: %s error=%s", surface, details, error, exc_info=error)

    @staticmethod
    def is_expected(error: BaseException) -> bool:
        """Return whether an error is one we already know how to explain to a user."""
        return isinstance(error, UserFacingError)

    @staticmethod
    def to_user_message(error: BaseException) -> str:
        """Return the text that is safe to show a user for a caught exception."""
        if isinstance(error, UserFacingError):
            return str(error)
        return "Something went wrong. This has been logged."
