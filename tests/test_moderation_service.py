from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from owlin_bot.models.moderation import ActionResult, MessageEvent
from owlin_bot.services.moderation_service import ModerationService
from owlin_bot.settings import Settings


@dataclass
class FakeModerationActions:
    delete_result: ActionResult = field(default_factory=lambda: ActionResult(succeeded=True))
    ban_result: ActionResult = field(default_factory=lambda: ActionResult(succeeded=True))
    delete_calls: list[dict[str, object]] = field(default_factory=list)
    ban_calls: list[dict[str, object]] = field(default_factory=list)

    async def delete_message(self, channel_id, message_id):
        self.delete_calls.append(
            {"channel_id": channel_id, "message_id": message_id}
        )
        return self.delete_result

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
        "message_id": 123,
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
async def test_trigger_deletes_triggering_message():
    actions = FakeModerationActions()

    await ModerationService(make_settings(), actions).handle_message(make_event())

    assert actions.delete_calls == [{"channel_id": 7, "message_id": 123}]
    assert actions.ban_calls == []


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

    assert actions.delete_calls == []
    assert actions.ban_calls == []


@pytest.mark.asyncio
async def test_protected_member_can_be_moderated_when_protection_is_disabled():
    actions = FakeModerationActions()

    await ModerationService(
        make_settings(protect_administrators=False), actions
    ).handle_message(make_event(author_is_administrator=True))

    assert len(actions.delete_calls) == 1


@pytest.mark.asyncio
async def test_delete_error_is_reported():
    actions = FakeModerationActions(
        delete_result=ActionResult(succeeded=False, error="delete failed"),
    )

    await ModerationService(make_settings(), actions).handle_message(make_event())
    assert len(actions.delete_calls) == 1


@pytest.mark.asyncio
async def test_unexpected_action_error_is_not_hidden():
    class BrokenActions(FakeModerationActions):
        async def delete_message(
            self,
            channel_id,
            message_id,
        ):
            raise RuntimeError("programming error")

    with pytest.raises(RuntimeError, match="programming error"):
        await ModerationService(make_settings(), BrokenActions()).handle_message(make_event())
