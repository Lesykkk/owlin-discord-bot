from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from owlin_bot.modules.publishing.models import PublishRequest
from owlin_bot.modules.publishing.service import PublishingService
from owlin_bot.app.constants import PUBLISH_COMMAND_CHANNEL_ID, PUBLISH_EMBED_COLOR
from owlin_bot.app.settings import Settings
from owlin_bot.shared.errors import RequestError


@dataclass
class FakePublishingActions:
    error: Exception | None = None
    calls: list[dict[str, object]] = field(default_factory=list)

    async def send_embed(self, channel_id, content, *, color):
        self.calls.append(
            {"channel_id": channel_id, "content": content, "color": color}
        )
        if self.error is not None:
            raise self.error


def make_service(actions: FakePublishingActions) -> PublishingService:
    settings = Settings(
        discord_token="test-token",
        restricted_channel_id=7,
        publish_command_channel_id=PUBLISH_COMMAND_CHANNEL_ID,
    )
    return PublishingService(settings, actions)


def make_request(**overrides) -> PublishRequest:
    values = {
        "source_guild_id": 42,
        "source_channel_id": PUBLISH_COMMAND_CHANNEL_ID,
        "target_guild_id": 42,
        "target_channel_id": 99,
        "content": "**Hello**\n\n*world*",
    }
    values.update(overrides)
    return PublishRequest(**values)


@pytest.mark.asyncio
async def test_publish_sends_embed_with_original_content_and_color():
    actions = FakePublishingActions()

    await make_service(actions).publish(make_request())

    assert actions.calls == [
        {
            "channel_id": 99,
            "content": "**Hello**\n\n*world*",
            "color": PUBLISH_EMBED_COLOR,
        }
    ]


@pytest.mark.parametrize(
    "overrides",
    [
        {"source_channel_id": 123},
        {"source_guild_id": 1},
        {"target_guild_id": 1},
        {"content": "   "},
    ],
)
@pytest.mark.asyncio
async def test_invalid_publish_request_does_not_send_embed(overrides):
    actions = FakePublishingActions()

    with pytest.raises(RequestError):
        await make_service(actions).publish(make_request(**overrides))
    assert actions.calls == []


@pytest.mark.asyncio
async def test_publish_returns_discord_action_error():
    actions = FakePublishingActions(error=RuntimeError("send failed"))

    with pytest.raises(RuntimeError, match="send failed"):
        await make_service(actions).publish(make_request())
