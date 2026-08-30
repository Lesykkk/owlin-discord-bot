"""Decorator for discord.ext.tasks loops that must never die silently."""

from __future__ import annotations

import functools
from collections.abc import Awaitable, Callable

from owlin_bot.app.error_handling.manager import ErrorReportingManager


def guarded(
    name: str, manager: ErrorReportingManager
) -> Callable[[Callable[[], Awaitable[None]]], Callable[[], Awaitable[None]]]:
    """Wrap a tasks.loop body so a bug in it reports instead of raising.

    A tasks.loop that lets an exception escape its body stops forever with no
    automatic restart. This decorator is a supervisor boundary around a task
    body we cannot inspect in advance, so it deliberately catches the broad
    `Exception` rather than a specific list: the whole point is that no bug in
    that body should ever be allowed to kill the schedule. `BaseException` is
    intentionally NOT caught, so asyncio.CancelledError still propagates and
    shutdown/cancellation keeps working correctly.
    """

    def decorator(body: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        @functools.wraps(body)
        async def wrapper() -> None:
            try:
                await body()
            except Exception as error:  # pylint: disable=broad-exception-caught
                # A task body has no "known, already-friendly" exceptions of its
                # own, so anything reaching here is always worth a full traceback.
                manager.report(surface=f"task:{name}", error=error, expected=False)

        return wrapper

    return decorator
