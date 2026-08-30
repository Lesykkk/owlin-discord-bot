"""Correlation id (flow id) propagation for structured logging."""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar

_flow_id: ContextVar[str] = ContextVar("flow_id", default="-")


def new_flow_id() -> str:
    """Generate and bind a short correlation id for the current async task."""
    flow_id = uuid.uuid4().hex[:8]
    _flow_id.set(flow_id)
    return flow_id


def bind_flow_id(flow_id: str) -> None:
    """Bind an existing correlation id, e.g. a Discord message or interaction id."""
    _flow_id.set(flow_id)


def current_flow_id() -> str:
    """Return the correlation id bound to the current async task, if any."""
    return _flow_id.get()


class FlowIdLogFilter(logging.Filter):
    """Stamp every log record with the current flow id."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Attach the current flow id to a log record before it is formatted."""
        record.flow_id = _flow_id.get()
        return True
