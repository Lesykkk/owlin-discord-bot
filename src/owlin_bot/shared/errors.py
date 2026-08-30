"""Errors shared across bot modules."""

from __future__ import annotations


class OwlinError(Exception):
    """Base for every domain-specific error raised by the bot."""


class UserFacingError(OwlinError):
    """An error whose message is safe to show directly to a Discord user."""


class RequestError(UserFacingError):
    """Expected error caused by a user's request."""


class TransientError(OwlinError):
    """A retryable failure, such as a Discord or network hiccup."""


class IntegrationError(OwlinError):
    """A third-party integration returned something unexpected."""
