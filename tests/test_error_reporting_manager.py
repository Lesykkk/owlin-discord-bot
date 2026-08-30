from __future__ import annotations

from owlin_bot.app.error_handling.manager import ErrorReportingManager
from owlin_bot.shared.errors import RequestError, TransientError


def test_user_facing_error_message_is_shown_verbatim():
    manager = ErrorReportingManager()

    message = manager.to_user_message(RequestError("Publishing content cannot be empty."))

    assert message == "Publishing content cannot be empty."


def test_unexpected_error_gets_generic_message():
    manager = ErrorReportingManager()

    message = manager.to_user_message(RuntimeError("boom"))

    assert message == "Something went wrong. This has been logged."


def test_is_expected_matches_user_facing_error_only():
    manager = ErrorReportingManager()

    assert manager.is_expected(RequestError("bad request")) is True
    assert manager.is_expected(TransientError("network hiccup")) is False
    assert manager.is_expected(RuntimeError("boom")) is False


def test_unexpected_report_includes_a_traceback(caplog):
    manager = ErrorReportingManager()

    try:
        raise RuntimeError("boom")
    except RuntimeError as error:
        manager.report(surface="command", error=error, expected=False, command="publish", user=99)

    assert "command error:" in caplog.text
    assert "command=publish" in caplog.text
    assert "user=99" in caplog.text
    assert "error=boom" in caplog.text
    assert "Traceback" in caplog.text


def test_expected_report_has_no_traceback_noise(caplog):
    manager = ErrorReportingManager()
    caplog.set_level("INFO")

    manager.report(
        surface="command",
        error=RequestError("Publishing content cannot be empty."),
        expected=True,
        command="publish",
    )

    assert "command error:" in caplog.text
    assert "error=Publishing content cannot be empty." in caplog.text
    assert "Traceback" not in caplog.text
