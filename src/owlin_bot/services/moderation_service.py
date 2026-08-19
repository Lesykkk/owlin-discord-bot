"""Business rules for restricted-channel moderation."""

from __future__ import annotations

import logging
from typing import Protocol

from owlin_bot.constants import MODERATION_REASON
from owlin_bot.models.moderation import ActionResult, MessageEvent
from owlin_bot.settings import Settings

logger = logging.getLogger(__name__)


class ModerationActions(Protocol):
    """Discord operations required by ModerationService."""

    async def delete_message(self, channel_id: int, message_id: int) -> ActionResult:
        """Delete one message from a Discord channel."""
        raise NotImplementedError

    async def ban_member(
        self,
        guild_id: int,
        member_id: int,
        *,
        reason: str,
        delete_message_seconds: int,
    ) -> ActionResult:
        """Ban a member and delete their recent guild messages."""
        raise NotImplementedError


class ModerationService:
    """Applies moderation rules and coordinates moderation actions."""

    def __init__(self, settings: Settings, actions: ModerationActions) -> None:
        self._settings = settings
        self._actions = actions

    async def handle_message(self, event: MessageEvent) -> None:
        """Dispatch a message to the configured moderation rules."""
        await self._handle_restricted_channel_spam(event)

    async def _handle_restricted_channel_spam(self, event: MessageEvent) -> None:
        """Detect spam in the restricted channel and ban its author."""
        skip_reason = self._get_spam_skip_reason(event)
        if skip_reason is not None:
            if skip_reason == "protected_member":
                logger.warning(
                    "Spam moderation ignored for protected member %s",
                    event.author_id,
                )
            return

        # _get_spam_skip_reason rejects direct messages, so guild_id is present here.
        guild_id = event.guild_id
        if guild_id is None:
            raise RuntimeError("Moderation event must belong to a guild")

        ban_result = await self._actions.ban_member(
            guild_id,
            event.author_id,
            reason=MODERATION_REASON,
            delete_message_seconds=self._settings.cleanup_window_seconds,
        )
        if not ban_result.succeeded:
            logger.error(
                "Failed to ban spam author %s in guild %s: %s",
                event.author_id,
                guild_id,
                ban_result.error,
            )
            return

        logger.info(
            "Restricted-channel spam author %s was banned in guild %s",
            event.author_id,
            guild_id,
        )

    def _get_spam_skip_reason(self, event: MessageEvent) -> str | None:
        """Return why the restricted-channel spam rule should be skipped."""
        if event.guild_id is None:
            return "direct_message"
        if event.author_is_bot:
            return "bot_message"
        if event.channel_id != self._settings.watched_channel_id:
            return "different_channel"
        if self._settings.protect_administrators and (
            event.author_is_server_owner or event.author_is_administrator
        ):
            return "protected_member"
        return None
