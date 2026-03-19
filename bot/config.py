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
            self.token: str = os.environ["DISCORD_TOKEN"]
        except KeyError as exc:
            raise RuntimeError("DISCORD_TOKEN environment variable is required") from exc

        # Basic bot configuration
        self.guild_id: int | None = (
            int(gid) if (gid := os.getenv("DISCORD_GUILD_ID")) else None
        )

        # Enable only what we need. Slash commands don't require message content.
        self.intents: discord.Intents = discord.Intents.default()
        self.intents.guilds = True


settings = Settings()

