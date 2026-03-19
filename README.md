# disc-bot (discord.py)

Minimal, modular **Discord bot template** built with `discord.py` using **slash commands** (`app_commands` / `CommandTree`).

## What you get

- A clean starting structure (`bot/` package + feature cogs/extensions)
- `/ping` slash command (ephemeral reply)
- Safe command syncing using `setup_hook`:
  - Guild sync for fast iteration (when `DISCORD_GUILD_ID` is set)
  - Sync to all guilds for fast development (when `DISCORD_SYNC_ALL_GUILDS=1`)
  - Global sync otherwise
- Secrets via root `.env` + `.env.example`

## Prerequisites

- Python 3.10+
- A Discord application + bot token
- The bot invited to a server with the correct OAuth scopes

## Setup

1. Install dependencies:

   ```powershell
   cd E:\disc-bot
   python -m pip install -r requirements.txt
   ```

2. Create your secrets file:

   - Copy `E:\disc-bot\.env.example` to `E:\disc-bot\.env`
   - Fill in `DISCORD_TOKEN`
   - (Optional) set `DISCORD_GUILD_ID` so slash commands sync quickly while developing
   - (Optional) set `DISCORD_SYNC_ALL_GUILDS=1` to sync/copy slash commands to every guild the bot is currently in

3. Invite the bot with the right scopes:

- OAuth scopes must include:
  - `bot`
  - `applications.commands`

You can generate this in the Discord Developer Portal (OAuth2 URL Generator) or you can use the invite URL generated there.

## Run the bot

From the repo root:

```powershell
python -m bot.main
```

The bot will:

- Load extensions from `DiscBot.EXTENSIONS`
- Sync slash commands during `setup_hook`

### Sync behavior (important)

- If `DISCORD_SYNC_ALL_GUILDS=1`: the bot copies/syncs slash commands to **every guild it is in** on startup (fastest for “sync everywhere” during dev).
- Else if `DISCORD_GUILD_ID` is set: commands sync to that guild and appear quickly.
- Else: commands sync globally and may take up to ~1 hour to propagate.

## Project structure

```text
disc-bot/
  bot/
    __init__.py
    main.py                 # DiscBot client + extension loading + command sync
    config.py               # loads .env + exposes `settings`
    logging_config.py       # logging setup
    cogs/
      __init__.py
      core.py               # /ping command (example cog)
  tests/                   # (optional for future)
  requirements.txt
  .env.example
  .gitignore
  AGENTS.md
  README.md
```

## How to add new stuff

### Add a new cog (recommended)

1. Create a new file under `bot/cogs/`, for example:
   - `bot/cogs/moderation.py`
2. Define a `commands.Cog` class.
3. Add slash commands using `@app_commands.command(...)`.
4. Implement the async `setup(...)` function that calls `bot.add_cog(...)`.

The `DiscBot.setup_hook` loads extensions listed in:

```python
DiscBot.EXTENSIONS
```

So after creating `bot/cogs/moderation.py`, also add the extension path:

```python
"bot.cogs.moderation",
```

### Example: add another slash command

In `bot/cogs/core.py` (or a new cog), add:

```python
from discord import app_commands
import discord
from discord.ext import commands

class MyCog(commands.Cog):
    @app_commands.command(name="hello", description="Say hello")
    async def hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hello!", ephemeral=True)
```

Then ensure the extension is loaded via `DiscBot.EXTENSIONS`.

## Conventions (so commands sync correctly)

- Keep slash commands defined in extensions/cogs that are loaded during `setup_hook`.
- Don’t rely on message commands for new features; prefer slash commands going forward.
- Make sure the bot has the `applications.commands` scope when invited.
- If you’re using guild/global syncing and don’t see updates immediately, restart the bot so it runs `sync()` again (kicking/re-inviting is usually unnecessary).

## Notes / next steps

- Add unit tests for service logic as the bot grows.
- Add centralized error handling once you have more commands.
- Add more cogs (one per feature area) rather than growing a single file.

