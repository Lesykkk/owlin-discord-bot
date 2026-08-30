from __future__ import annotations

import logging

from owlin_bot.app.context import FlowIdLogFilter, bind_flow_id, current_flow_id, new_flow_id


def test_bind_flow_id_is_visible_via_current_flow_id():
    bind_flow_id("abc123")

    assert current_flow_id() == "abc123"


def test_new_flow_id_generates_and_binds_a_short_id():
    flow_id = new_flow_id()

    assert current_flow_id() == flow_id
    assert len(flow_id) == 8


def test_filter_stamps_the_current_flow_id_onto_records():
    bind_flow_id("xyz789")
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "msg", None, None)

    result = FlowIdLogFilter().filter(record)

    assert result is True
    assert record.flow_id == "xyz789"
