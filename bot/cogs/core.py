import logging

import discord
from discord import app_commands
from discord.ext import commands


class Core(commands.Cog):
    """Core commands and utilities."""

    def __init__(self, bot: commands.Bot | discord.Client) -> None:
        self.bot = bot
        self.log = logging.getLogger(__name__)

    @app_commands.command(name="ping", description="Check if the bot is responsive.")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Simple health check slash command."""
        await interaction.response.send_message("Pong!", ephemeral=True)


async def setup(bot: commands.Bot | discord.Client) -> None:
    await bot.add_cog(Core(bot))

