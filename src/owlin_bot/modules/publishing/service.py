"""Application service for publishing formatted Discord messages."""

from __future__ import annotations

from typing import Protocol

from owlin_bot.app.constants import PUBLISH_EMBED_COLOR
from owlin_bot.app.settings import Settings
from owlin_bot.modules.publishing.models import PublishRequest
from owlin_bot.shared.errors import RequestError


class PublishingActions(Protocol):
    """Discord operations required by publishing."""

    async def send_embed(
        self,
        channel_id: int,
        content: str,
        *,
        color: int,
    ) -> None:
        """Send formatted content to a Discord channel."""
        raise NotImplementedError


class PublishingService:
    """Validate publish requests and send formatted messages."""

    def __init__(self, settings: Settings, actions: PublishingActions) -> None:
        self._settings = settings
        self._actions = actions

    async def publish(self, request: PublishRequest) -> None:
        """Publish a request when it satisfies the publishing rules."""
        self._validate(request)
        await self._actions.send_embed(
            request.target_channel_id,
            request.content,
            color=PUBLISH_EMBED_COLOR,
        )

    def _validate(self, request: PublishRequest) -> None:
        """Raise a user-facing error when a request is invalid."""
        if request.source_channel_id != self._settings.publish_command_channel_id:
            raise RequestError("Publishing commands are not allowed in this channel.")
        if request.source_guild_id != request.target_guild_id:
            raise RequestError("The target channel must belong to the same server.")
        if not request.content.strip():
            raise RequestError("Publishing content cannot be empty.")
