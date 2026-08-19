from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import pytest

from owlin_bot.constants import MODERATION_REASON
from owlin_bot.models.moderation import ActionResult, MessageEvent
from owlin_bot.services.moderation_service import ModerationService
from owlin_bot.settings import Settings


@dataclass
class FakeModerationActions:
    ban_result: ActionResult = field(default_factory=lambda: ActionResult(succeeded=True))
    ban_calls: list[dict[str, object]] = field(default_factory=list)

    async def ban_member(self, guild_id, member_id, *, reason, delete_message_seconds):
        self.ban_calls.append(
            {
                "guild_id": guild_id,
                "member_id": member_id,
                "reason": reason,
                "delete_message_seconds": delete_message_seconds,
            }
        )
        return self.ban_result


def make_settings(**overrides) -> Settings:
    values = {
        "discord_token": "test-token",
        "watched_channel_id": 7,
        "cleanup_window_seconds": 300,
        "protect_administrators": True,
    }
    values.update(overrides)
    return Settings(**values)


def make_event(**overrides) -> MessageEvent:
    values = {
        "guild_id": 42,
        "channel_id": 7,
        "author_id": 99,
        "author_is_bot": False,
        "author_is_server_owner": False,
        "author_is_administrator": False,
        "created_at": datetime(2026, 8, 19, 12, 5, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return MessageEvent(**values)


@pytest.mark.asyncio
async def test_trigger_bans_member_and_deletes_last_five_minutes():
    actions = FakeModerationActions()

    await ModerationService(make_settings(), actions).handle_message(make_event())

    assert actions.ban_calls == [
        {
            "guild_id": 42,
            "member_id": 99,
            "reason": MODERATION_REASON,
            "delete_message_seconds": 300,
        }
    ]


@pytest.mark.parametrize(
    ("event_overrides", "reason"),
    [
        ({"guild_id": None}, "direct_message"),
        ({"author_is_bot": True}, "bot_message"),
        ({"channel_id": 8}, "different_channel"),
        ({"author_is_server_owner": True}, "protected_member"),
        ({"author_is_administrator": True}, "protected_member"),
    ],
)
@pytest.mark.asyncio
async def test_ignored_messages_do_not_trigger_actions(event_overrides, reason):
    actions = FakeModerationActions()

    await ModerationService(make_settings(), actions).handle_message(
        make_event(**event_overrides)
    )

    assert actions.ban_calls == []


@pytest.mark.asyncio
async def test_protected_member_can_be_moderated_when_protection_is_disabled():
    actions = FakeModerationActions()

    await ModerationService(
        make_settings(protect_administrators=False), actions
    ).handle_message(make_event(author_is_administrator=True))

    assert len(actions.ban_calls) == 1


@pytest.mark.asyncio
async def test_ban_error_is_reported():
    actions = FakeModerationActions(
        ban_result=ActionResult(succeeded=False, error="ban failed"),
    )

    await ModerationService(make_settings(), actions).handle_message(make_event())
    assert len(actions.ban_calls) == 1


@pytest.mark.asyncio
async def test_unexpected_action_error_is_not_hidden():
    class BrokenActions(FakeModerationActions):
        async def ban_member(
            self,
            guild_id,
            member_id,
            *,
            reason,
            delete_message_seconds,
        ):
            raise RuntimeError("programming error")

    with pytest.raises(RuntimeError, match="programming error"):
        await ModerationService(make_settings(), BrokenActions()).handle_message(make_event())
