"""Shared helper for answering a Discord interaction from any error handler."""

from __future__ import annotations

import discord


async def respond_to_interaction(interaction: discord.Interaction, message: str) -> None:
    """Send an ephemeral reply to an interaction, whether or not it was already acknowledged.

    Discord requires the first acknowledgement of an interaction within 3
    seconds; after that, only interaction.followup can be used. This picks
    whichever one is still valid.
    """
    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
        # The interaction token can already be dead (e.g. expired after 15
        # minutes). Nothing left to notify the user with; the report() call
        # made before this was still logged, so the failure is not silent.
        pass
