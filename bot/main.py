import asyncio
import logging

import discord
from discord import app_commands

from .config import settings
from .logging_config import setup_logging


class DiscBot(discord.Client):
    """Discord client configured for slash commands via CommandTree."""

    EXTENSIONS: tuple[str, ...] = (
        "bot.cogs.core",
    )

    def __init__(self) -> None:
        setup_logging()
        super().__init__(intents=settings.intents)
        self.tree = app_commands.CommandTree(self)
        self.log = logging.getLogger(__name__)

    async def setup_hook(self) -> None:
        """Async initialization hook.

        This is the recommended place to:
        - Load extensions.
        - Perform initial application command sync.
        """
        # Load all feature extensions.
        for ext in self.EXTENSIONS:
            await self.load_extension(ext)

        # Sync application commands.
        # Prefer a single development guild for fast iteration when configured.
        if settings.guild_id is not None:
            guild = discord.Object(id=settings.guild_id)
            self.log.info("Syncing application commands to guild %s", settings.guild_id)
            await self.tree.sync(guild=guild)
        else:
            # Global sync can take up to ~1 hour to propagate.
            self.log.info("Syncing global application commands")
            await self.tree.sync()

    async def on_ready(self) -> None:
        self.log.info("Logged in as %s (ID: %s)", self.user, getattr(self.user, "id", "?"))


async def main() -> None:
    client = DiscBot()
    async with client:
        await client.start(settings.token)


if __name__ == "__main__":
    asyncio.run(main())

