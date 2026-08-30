"""Shared behaviour for translating a caught exception into a user-facing message."""

from __future__ import annotations

from abc import ABC, abstractmethod

from owlin_bot.app.error_handling.manager import ErrorReportingManager


class ErrorSurfaceHandler(ABC):
    """Template for one Discord error surface: unwrap, classify, then respond.

    A subclass only has to describe which library exceptions on its surface
    already deserve a friendly message (`_known_error_message`); everything
    else falls back to `ErrorReportingManager.to_user_message`.
    """

    def __init__(self, manager: ErrorReportingManager) -> None:
        self._manager = manager

    @staticmethod
    def _unwrap(error: BaseException) -> BaseException:
        """Return the exception that was actually raised, unwrapping an *InvokeError.

        Both discord.ext.commands and discord.app_commands wrap whatever a
        command body raises in their own *InvokeError, exposing the real
        exception as `.original`. Checking for that attribute (instead of
        naming either wrapper class) works for both surfaces at once.
        """
        return getattr(error, "original", error)

    def _classify(self, error: BaseException) -> tuple[str, bool]:
        """Return (message, expected) for an error.

        `expected=True` means this is a routine, already-understood mistake
        (a known library exception, or one of our own UserFacingError
        subclasses) and does not need a full traceback in the logs.
        """
        known = self._known_error_message(error)
        if known is not None:
            return known, True
        return self._manager.to_user_message(error), self._manager.is_expected(error)

    @abstractmethod
    def _known_error_message(self, error: BaseException) -> str | None:
        """Return a friendly message for a library exception specific to this surface.

        Return None to fall back to the generic UserFacingError/unexpected-error message.
        """
