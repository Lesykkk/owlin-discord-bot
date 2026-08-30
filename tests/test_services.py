from __future__ import annotations

from owlin_bot.app.services import Services


def test_services_holds_whatever_each_module_assigns_to_it():
    services = Services()
    moderation = object()
    publishing = object()

    services.moderation = moderation
    services.publishing = publishing

    assert services.moderation is moderation
    assert services.publishing is publishing
