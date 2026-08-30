from __future__ import annotations

import pytest

from owlin_bot.app.error_handling.manager import ErrorReportingManager
from owlin_bot.app.error_handling.task_supervisor import guarded


@pytest.mark.asyncio
async def test_successful_body_runs_without_reporting(caplog):
    calls: list[str] = []

    @guarded("ping", ErrorReportingManager())
    async def body() -> None:
        calls.append("ran")

    await body()

    assert calls == ["ran"]
    assert caplog.text == ""


@pytest.mark.asyncio
async def test_failing_body_is_reported_instead_of_raised(caplog):
    @guarded("ping", ErrorReportingManager())
    async def body() -> None:
        raise RuntimeError("boom")

    await body()

    assert "task:ping error:" in caplog.text
    assert "error=boom" in caplog.text
