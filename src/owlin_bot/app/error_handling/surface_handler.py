"""Shared behaviour for translating a caught exception into a user-facing message."""

from __future__ import annotations

from abc import ABC, abstractmethod

from owlin_bot.app.error_handling.manager import ErrorReportingManager


class ErrorSurfaceHandler(ABC):
    """Template for one Discord error surface: unwrap, translate, then respond.

    A subclass only has to describe which library exceptions on its surface
    already deserve a friendly message (`_known_error_message`); everything
    else falls back to `ErrorReportingManager.to_user_message`.
    """

    def __init__(self, manager: ErrorReportingManager) -> None:
        self._manager = manager

    @staticmethod
    def _unwrap(error: BaseException) -> BaseException:
        """Return the exception that was actually raised, unwrapping an *InvokeError."""
        return getattr(error, "original", error)

    def _to_message(self, error: BaseException) -> str:
        """Return the response text for an error."""
        known = self._known_error_message(error)
        return known if known is not None else self._manager.to_user_message(error)

    @abstractmethod
    def _known_error_message(self, error: BaseException) -> str | None:
        """Return a friendly message for a library exception specific to this surface.

        Return None to fall back to the generic UserFacingError/unexpected-error message.
        """
