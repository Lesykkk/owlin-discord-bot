"""Business rules for restricted-channel moderation."""

from __future__ import annotations

import logging
from typing import Protocol

from owlin_bot.app.constants import MODERATION_REASON
from owlin_bot.app.settings import Settings
from owlin_bot.modules.moderation.models import MessageEvent

logger = logging.getLogger(__name__)


class ModerationActions(Protocol):
    """Discord operations required by moderation."""

    async def ban_member(
        self,
        guild_id: int,
        member_id: int,
        *,
        reason: str,
        delete_message_seconds: int,
    ) -> None:
        """Ban a member and delete their recent guild messages."""
        raise NotImplementedError

    async def unban_member(
        self,
        guild_id: int,
        member_id: int,
        *,
        reason: str,
    ) -> None:
        """Unban a member from a guild."""
        raise NotImplementedError


class ModerationService:
    """Apply moderation rules and coordinate moderation actions."""

    def __init__(self, settings: Settings, actions: ModerationActions) -> None:
        self._settings = settings
        self._actions = actions

    async def handle_message(self, event: MessageEvent) -> None:
        """Dispatch a message to the configured moderation rules."""
        await self._handle_restricted_channel_spam(event)

    async def _handle_restricted_channel_spam(self, event: MessageEvent) -> None:
        """Detect spam in the restricted channel and ban its author."""
        if (
            event.guild_id is None
            or event.author_is_bot
            or event.channel_id != self._settings.restricted_channel_id
            or event.author_is_server_owner
            or event.author_is_administrator
        ):
            return

        await self._actions.ban_member(
            event.guild_id,
            event.author_id,
            reason=MODERATION_REASON,
            delete_message_seconds=self._settings.cleanup_window_seconds,
        )
        await self._actions.unban_member(
            event.guild_id,
            event.author_id,
            reason=MODERATION_REASON,
        )
        logger.info(
            "Moderation: action=ban_unban guild=%s user=%s channel=%s",
            event.guild_id,
            event.author_id,
            event.channel_id,
        )
