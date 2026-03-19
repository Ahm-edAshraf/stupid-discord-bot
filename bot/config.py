import os
from pathlib import Path

import discord
from dotenv import load_dotenv


class Settings:
    """Central configuration object for the bot."""

    def __init__(self) -> None:
        # Load local secrets from a root `.env` file (if present).
        # This keeps environment-specific secrets out of the codebase.
        base_dir = Path(__file__).resolve().parent.parent
        load_dotenv(base_dir / ".env")

        # Required
        try:
            # `.env` values can accidentally include whitespace; strip to avoid invalid tokens.
            self.token = os.environ["DISCORD_TOKEN"].strip()
        except KeyError as exc:
            raise RuntimeError("DISCORD_TOKEN environment variable is required") from exc

        if not self.token:
            raise RuntimeError("DISCORD_TOKEN is empty after trimming. Check your .env formatting.")

        # Discord bot tokens are typically much longer than 32 chars.
        # If it's short, it's very likely the wrong value (OAuth token, client secret, etc).
        if len(self.token) < 40:
            raise RuntimeError(
                "DISCORD_TOKEN looks too short (len < 40). Did you paste the Bot token from "
                "Discord Developer Portal (not OAuth token / client secret)?"
            )

        # Basic bot configuration
        self.guild_id: int | None = (
            int(gid) if (gid := os.getenv("DISCORD_GUILD_ID")) else None
        )

        # Enable only what we need.
        # Slash commands don't require message content (privileged), but the
        # commands extension may still expect the `messages` intent.
        self.intents: discord.Intents = discord.Intents.default()
        self.intents.guilds = True
        self.intents.messages = True

        # If enabled, the bot will copy/sync commands to every guild it is in
        # on startup (after `on_ready`).
        #
        # This is the fastest way to get updates across multiple servers during
        # development, avoiding global command propagation delays.
        self.sync_all_guilds: bool = os.getenv("DISCORD_SYNC_ALL_GUILDS", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }


settings = Settings()

