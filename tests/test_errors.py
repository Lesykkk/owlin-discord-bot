from __future__ import annotations

from types import SimpleNamespace

import pytest
from discord.ext import commands

from owlin_bot.app.error_handler import ErrorHandler
from owlin_bot.shared.errors import RequestError


class FakeDiscordClient:
    def __init__(self) -> None:
        self.messages: list[tuple[int, str]] = []

    async def send_message(self, channel_id: int, content: str) -> None:
        self.messages.append((channel_id, content))


def make_context(
    channel_id: int = 42,
    *,
    command_name: str | None = "publish",
    invoked_with: str = "publish",
) -> SimpleNamespace:
    return SimpleNamespace(
        channel=SimpleNamespace(id=channel_id),
        command=(
            SimpleNamespace(qualified_name=command_name)
            if command_name is not None
            else None
        ),
        invoked_with=invoked_with,
        author=SimpleNamespace(id=99),
        guild=SimpleNamespace(id=42),
    )


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (
            commands.NoPrivateMessage(),
            "This command can only be used in a server.",
        ),
        (
            commands.CheckFailure(),
            "You do not have permission to use this command.",
        ),
        (
            commands.MissingRequiredArgument(
                SimpleNamespace(name="content", displayed_name="content")
            ),
            "This command is missing required arguments.",
        ),
        (commands.BadArgument(), "Invalid command arguments."),
        (RequestError("Publishing content cannot be empty."), "Publishing content cannot be empty."),
    ],
)
@pytest.mark.asyncio
async def test_expected_command_errors_are_sent_to_user(error, message):
    discord_client = FakeDiscordClient()
    handler = ErrorHandler(discord_client)

    await handler.handle_command_error(make_context(), error)

    assert discord_client.messages == [(42, message)]


@pytest.mark.asyncio
async def test_wrapped_request_error_is_sent_to_user():
    discord_client = FakeDiscordClient()
    handler = ErrorHandler(discord_client)
    error = commands.CommandInvokeError(
        RequestError("The target channel must belong to the same server.")
    )

    await handler.handle_command_error(make_context(7), error)

    assert discord_client.messages == [
        (7, "The target channel must belong to the same server.")
    ]


@pytest.mark.asyncio
async def test_command_not_found_is_logged_without_response(caplog):
    discord_client = FakeDiscordClient()
    handler = ErrorHandler(discord_client)

    await handler.handle_command_error(
        make_context(command_name=None, invoked_with="missing"),
        commands.CommandNotFound(),
    )

    assert discord_client.messages == []
    assert "Command error: command=missing user=99 guild=42" in caplog.text


@pytest.mark.asyncio
async def test_unexpected_command_error_is_logged_without_response(caplog):
    discord_client = FakeDiscordClient()
    handler = ErrorHandler(discord_client)
    error = commands.CommandInvokeError(RuntimeError("broken"))

    await handler.handle_command_error(make_context(), error)

    assert discord_client.messages == []
    assert "Command error: command=publish user=99 guild=42 error=broken" in caplog.text


@pytest.mark.asyncio
async def test_event_error_is_logged_without_response(caplog):
    discord_client = FakeDiscordClient()
    handler = ErrorHandler(discord_client)

    try:
        raise RuntimeError("broken event")
    except RuntimeError:
        await handler.handle_event_error("on_message")

    assert discord_client.messages == []
    assert "Event error: event=on_message error=broken event" in caplog.text
