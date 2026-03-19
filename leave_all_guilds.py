# leave_all_guilds.py
import os
import asyncio
from pathlib import Path

import discord
from dotenv import load_dotenv


async def main() -> None:
    # Loads E:\disc-bot\.env
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")

    token = os.environ["DISCORD_TOKEN"].strip()

    # Safety guard
    if os.getenv("DISCORD_LEAVE_ALL", "").upper() != "YES":
        raise RuntimeError("Set DISCORD_LEAVE_ALL=YES to confirm you want to leave all guilds.")

    intents = discord.Intents.none()
    intents.guilds = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        guilds = list(client.guilds)
        print(f"Leaving {len(guilds)} guild(s)...")

        for g in guilds:
            print(f"Leaving: {g.name} ({g.id})")
            try:
                await g.leave()
                await asyncio.sleep(1)  # be gentle with rate limits
            except Exception as exc:
                print(f"Failed to leave {g.id}: {exc!r}")

        await client.close()

    await client.start(token)


if __name__ == "__main__":
    asyncio.run(main())