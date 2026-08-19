"""Reusable authorization checks for Discord commands."""

from __future__ import annotations

from collections.abc import Callable

from discord.ext import commands

type CommandCheck = Callable[[commands.Context[commands.Bot]], bool]


def is_guild_context(context: commands.Context[commands.Bot]) -> bool:
    """Allow a command only when it was invoked on a Discord server."""
    return context.guild is not None


def is_server_owner(context: commands.Context[commands.Bot]) -> bool:
    """Allow a command only for the owner of the current server."""
    return context.guild is not None and context.author.id == context.guild.owner_id


def is_administrator_or_owner(context: commands.Context[commands.Bot]) -> bool:
    """Allow a command for the server owner or an administrator."""
    if context.guild is None:
        return False
    if context.author.id == context.guild.owner_id:
        return True

    permissions = getattr(context.author, "guild_permissions", None)
    return bool(permissions and permissions.administrator)


def is_in_channel(channel_id: int) -> CommandCheck:
    """Create a check that allows a command only in one channel."""

    def check(context: commands.Context[commands.Bot]) -> bool:
        return context.channel.id == channel_id

    return check
