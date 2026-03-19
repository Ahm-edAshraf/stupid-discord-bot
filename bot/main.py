import asyncio
import logging

import discord
from discord.ext import commands

from .config import settings
from .logging_config import setup_logging


class DiscBot(commands.Bot):
    """Discord client configured for slash commands via CommandTree."""

    EXTENSIONS: tuple[str, ...] = (
        "bot.cogs.core",
    )

    def __init__(self) -> None:
        setup_logging()
        # `commands.Bot` provides `load_extension` and owns the app command tree.
        # Use a mention-based prefix so we don't rely on privileged message content.
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=settings.intents)
        self.log = logging.getLogger(__name__)
        self._did_sync_all_guilds = False

    async def setup_hook(self) -> None:
        """Async initialization hook.

        This is the recommended place to:
        - Load extensions.
        - Perform initial application command sync.
        """
        # Load all feature extensions.
        for ext in self.EXTENSIONS:
            await self.load_extension(ext)

        # Debug: log what the local command tree currently contains.
        # This helps diagnose "commands not updating" issues.
        local_command_names = [cmd.qualified_name for cmd in self.tree.get_commands()]
        self.log.info("Local app commands before sync: %s", local_command_names)

        # Sync application commands.
        # Fast path:
        # - If DISCORD_SYNC_ALL_GUILDS is enabled, we'll do guild syncing in on_ready
        #   (we need guilds available).
        # - Otherwise, use DISCORD_GUILD_ID for fast iteration, or global sync.
        if settings.sync_all_guilds:
            self.log.info("Deferring sync to on_ready (DISCORD_SYNC_ALL_GUILDS enabled)")
            return

        # Prefer a single development guild for fast iteration when configured.
        if settings.guild_id is not None:
            guild = discord.Object(id=settings.guild_id)
            self.log.info("Syncing application commands to guild %s", settings.guild_id)

            # Clear guild commands first to avoid stale commands lingering.
            # This is safe for dev-style guild sync and ensures updates/deletions are applied.
            if hasattr(self.tree, "clear_commands"):
                self.log.info("Clearing existing guild commands before sync")
                # `clear_commands` is part of discord.py's interactions API.
                maybe_coro = self.tree.clear_commands(guild=guild)
                # In some discord.py versions this may be sync; handle both.
                if asyncio.iscoroutine(maybe_coro):
                    await maybe_coro
                self.log.info("Cleared existing guild commands (if supported)")

            # Copy the (local) global commands to the dev guild so changes to
            # globally-defined slash commands show up immediately.
            # This avoids waiting for global command propagation.
            copy_result = self.tree.copy_global_to(guild=guild)
            if asyncio.iscoroutine(copy_result):
                await copy_result
            self.log.info("Copied global app commands to guild")

            self.log.info("Syncing guild app commands now")
            synced_commands = await self.tree.sync(guild=guild)
            synced_names = [
                getattr(cmd, "qualified_name", getattr(cmd, "name", str(cmd)))
                for cmd in synced_commands
            ]
            self.log.info("Synced guild app commands: %s", synced_names)
        else:
            # Global sync can take up to ~1 hour to propagate.
            self.log.info("Syncing global application commands")
            synced_commands = await self.tree.sync()
            synced_names = [
                getattr(cmd, "qualified_name", getattr(cmd, "name", str(cmd)))
                for cmd in synced_commands
            ]
            self.log.info("Synced global app commands: %s", synced_names)

    async def on_ready(self) -> None:
        self.log.info("Logged in as %s (ID: %s)", self.user, getattr(self.user, "id", "?"))

        if settings.sync_all_guilds and not self._did_sync_all_guilds:
            self._did_sync_all_guilds = True
            await self._sync_to_all_guilds()

    async def _sync_to_all_guilds(self) -> None:
        # Copy global commands to each guild and then sync for immediate updates.
        guilds = list(self.guilds)
        self.log.info("Syncing application commands to all %d guild(s)", len(guilds))

        if not guilds:
            self.log.warning(
                "No guilds found. Re-add the bot to at least one server, then restart to sync."
            )
            return

        for guild in guilds:
            try:
                self.log.info("Syncing guild %s (%s)", guild.name, guild.id)
                copy_result = self.tree.copy_global_to(guild=guild)
                if asyncio.iscoroutine(copy_result):
                    await copy_result

                synced_commands = await self.tree.sync(guild=guild)
                synced_names = [
                    getattr(cmd, "qualified_name", getattr(cmd, "name", str(cmd)))
                    for cmd in synced_commands
                ]
                self.log.info("Synced guild %s app commands: %s", guild.id, synced_names)
            except Exception as exc:
                self.log.error("Failed syncing guild %s: %r", guild.id, exc)


async def main() -> None:
    client = DiscBot()
    async with client:
        await client.start(settings.token)


if __name__ == "__main__":
    asyncio.run(main())

