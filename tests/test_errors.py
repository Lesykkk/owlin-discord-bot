from __future__ import annotations

from owlin_bot.shared.errors import (
    IntegrationError,
    OwlinError,
    RequestError,
    TransientError,
    UserFacingError,
)


def test_request_error_is_user_facing_and_owlin_error():
    error = RequestError("bad request")

    assert isinstance(error, UserFacingError)
    assert isinstance(error, OwlinError)


def test_transient_error_is_owlin_error_but_not_user_facing():
    error = TransientError("network hiccup")

    assert isinstance(error, OwlinError)
    assert not isinstance(error, UserFacingError)


def test_integration_error_is_owlin_error_but_not_user_facing():
    error = IntegrationError("unexpected response")

    assert isinstance(error, OwlinError)
    assert not isinstance(error, UserFacingError)
