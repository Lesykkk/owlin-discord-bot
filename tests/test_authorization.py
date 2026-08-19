from __future__ import annotations

from types import SimpleNamespace

import pytest

from owlin_bot.app.authorization import (
    is_administrator_or_owner,
    is_guild_context,
    is_in_channel,
    is_server_owner,
)


def make_context(*, guild_id: int | None = 42, author_id: int = 7, channel_id: int = 10):
    return SimpleNamespace(
        guild=(SimpleNamespace(id=guild_id, owner_id=7) if guild_id else None),
        author=SimpleNamespace(
            id=author_id,
            guild_permissions=SimpleNamespace(administrator=False),
        ),
        channel=SimpleNamespace(id=channel_id),
    )


def test_is_guild_context():
    assert is_guild_context(make_context()) is True
    assert is_guild_context(make_context(guild_id=None)) is False


def test_is_server_owner():
    assert is_server_owner(make_context()) is True
    assert is_server_owner(make_context(author_id=8)) is False
    assert is_server_owner(make_context(guild_id=None)) is False


def test_is_administrator_or_owner_allows_owner_and_administrator():
    assert is_administrator_or_owner(make_context()) is True

    context = make_context(author_id=8)
    context.author.guild_permissions.administrator = True
    assert is_administrator_or_owner(context) is True

    assert is_administrator_or_owner(make_context(author_id=8)) is False
    assert is_administrator_or_owner(make_context(guild_id=None)) is False


def test_is_in_channel():
    check = is_in_channel(10)

    assert check(make_context(channel_id=10)) is True
    assert check(make_context(channel_id=11)) is False
