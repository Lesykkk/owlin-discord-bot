from __future__ import annotations

from owlin_bot.app.error_handling.manager import ErrorReportingManager
from owlin_bot.shared.errors import RequestError


def test_user_facing_error_message_is_shown_verbatim():
    manager = ErrorReportingManager()

    message = manager.to_user_message(RequestError("Publishing content cannot be empty."))

    assert message == "Publishing content cannot be empty."


def test_unexpected_error_gets_generic_message():
    manager = ErrorReportingManager()

    message = manager.to_user_message(RuntimeError("boom"))

    assert message == "Something went wrong. This has been logged."


def test_report_logs_surface_and_context(caplog):
    manager = ErrorReportingManager()

    manager.report(surface="command", error=RuntimeError("boom"), command="publish", user=99)

    assert "command error:" in caplog.text
    assert "command=publish" in caplog.text
    assert "user=99" in caplog.text
    assert "error=boom" in caplog.text
