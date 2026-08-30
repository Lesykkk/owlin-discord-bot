"""Container for every application service, populated by its own module."""

from __future__ import annotations

from owlin_bot.modules.moderation.service import ModerationService
from owlin_bot.modules.publishing.service import PublishingService


class Services:
    """Every application service, set once by its owning module during setup_hook."""

    moderation: ModerationService
    publishing: PublishingService
