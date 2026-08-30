"""Error reporting and per-surface error handlers for the Discord bot.

Map of this package, roughly core -> surfaces:
- manager: ErrorReportingManager, the shared log/translate sink every surface reports through.
- surface_handler: ErrorSurfaceHandler, the shared unwrap/translate skeleton for
  command-shaped surfaces (CommandErrorHandler, AppCommandErrorHandler).
- interaction_reply: respond_to_interaction, the shared "answer this Interaction" helper.
- command_errors / app_command_errors: the two command-shaped surfaces (prefix, slash).
- view_errors: SafeView / SafeModal, for buttons/selects/modals.
- task_supervisor: guarded(), for discord.ext.tasks loops.

Only this file's exports below are meant to be imported from outside this package;
everything else here imports its siblings directly to avoid a cycle through here.
"""

from __future__ import annotations

from owlin_bot.app.error_handling.app_command_errors import AppCommandErrorHandler
from owlin_bot.app.error_handling.command_errors import CommandErrorHandler
from owlin_bot.app.error_handling.interaction_reply import respond_to_interaction
from owlin_bot.app.error_handling.manager import ErrorReportingManager
from owlin_bot.app.error_handling.surface_handler import ErrorSurfaceHandler
from owlin_bot.app.error_handling.task_supervisor import guarded
from owlin_bot.app.error_handling.view_errors import SafeModal, SafeView

__all__ = [
    "AppCommandErrorHandler",
    "CommandErrorHandler",
    "ErrorReportingManager",
    "ErrorSurfaceHandler",
    "SafeModal",
    "SafeView",
    "guarded",
    "respond_to_interaction",
]
