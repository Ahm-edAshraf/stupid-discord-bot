## Purpose
This document defines how AI and human contributors should build and maintain this Discord bot using `discord.py`, focusing on correctness, safety, maintainability, and long‑term reliability.

The project goal is to create a **modular, production‑ready Discord bot** with clean architecture, strong separation of concerns, and minimal tech debt.

---

## Overall Architecture
- **Bot core**
  - Use `discord.py` with the commands extension and (where needed) app commands.
  - Keep the entrypoint (`main.py`) thin: configure logging, load config, construct the bot, and load extensions/cogs.
- **Modularity**
  - Organize commands and listeners into **cogs** grouped by feature area (e.g. `Admin`, `Moderation`, `Fun`, `Events`).
  - Implement business logic in **services** (e.g. `services/reminders.py`, `services/moderation.py`) rather than directly in cogs.
  - Use **extensions** (`bot.load_extension(...)`) as the deployment unit for features.
- **Config & secrets**
  - All secrets (Discord token, DB credentials, API keys) come from **environment variables or a secret manager**, never hardcoded or committed.
  - Support multiple environments (dev, staging, prod) through env vars only; no per‑env hardcoded branches in code.

---

## Project Structure (Baseline)
Human and AI contributors should converge on something close to this layout:

- `bot/`
  - `main.py` – entrypoint, starts the bot and loads extensions
  - `config.py` – configuration and environment variable loading
  - `logging_config.py` – logging setup
  - `cogs/` – feature‑oriented cogs
  - `services/` – reusable business logic modules and integrations
  - `utils/` – helpers (checks, converters, formatting, error types)
- `tests/` – unit and integration tests
- `requirements.txt` – pinned dependencies
- `AGENTS.md` – this file

If a new feature does not fit cleanly into an existing cog or service, prefer **creating a new cog/service** over bloating an existing one.

---

## Coding Standards
- **Language & style**
  - Use **Python 3.10+** with type hints everywhere meaningful.
  - Follow **PEP 8** for style and **PEP 257** for docstrings where behavior is non‑obvious.
  - Prefer explicit, descriptive names over abbreviations.
- **Async & I/O**
  - Never perform **blocking I/O** (e.g. `requests`, file operations) directly in event handlers or commands.
  - Use async libraries where possible or run blocking I/O in an executor.
  - Always `await` coroutines; never ignore returned tasks unless explicitly designed as background work with proper error logging.
- **Error handling**
  - Treat exceptions as **expected vs unexpected**:
    - Expected (e.g. “user not found”, validation failure) → return a controlled result or send a friendly message.
    - Unexpected (e.g. programming errors, external outages) → log full details and send a generic error to the user.
  - Never expose stack traces or sensitive details in Discord messages.
- **Argument validation**
  - Validate all user input at the boundary (command parameters, interaction data).
  - Use converters, checks, and explicit validation functions; fail fast with clear messages.
- **Separation of concerns**
  - Cogs are for **Discord wiring** (commands, listeners), not business rules.
  - Services and utilities implement **domain logic**, reusable across commands.
  - Avoid circular dependencies; prefer passing dependencies into constructors or via a simple “services registry” on the bot object.

---

## Discord.py Best Practices
- **Intents**
  - Only enable required intents; avoid `Intents.all()` unless strictly necessary.
  - Keep intent configuration centralized in `config.py`.
- **Commands & app commands**
  - Keep command bodies short; delegate real work to services.
  - Use **cooldowns** for commands that can be spammed or expensive.
  - Use permission checks (bot and user) before performing sensitive actions.
  - Provide helpful usage info and error messages for bad input.
- **Slash commands & syncing**
  - Prefer **application commands (slash commands)** for all new user‑facing functionality.
  - Use a `discord.app_commands.CommandTree` attached to the bot/client for all slash commands.
  - Define commands with `@tree.command(...)` or within cogs using `app_commands.Command` and keep them small, delegating work to services.
  - Implement `setup_hook` on the bot/client subclass to perform initial `tree.sync(...)` calls after login but before connecting to the gateway.
  - During development, sync commands to a **single test guild** with `await tree.sync(guild=discord.Object(GUILD_ID))` for near‑instant updates.
  - For production, use **global commands** (no guild argument) and understand they may take up to an hour to propagate.
  - Ensure the bot is invited with both `bot` and `applications.commands` scopes, or commands will not appear.
- **Cogs & extensions**
  - Each cog should cover a **single responsibility or tightly related feature set**.
  - Use `async def setup(bot): await bot.add_cog(...)` in each extension module.
  - Avoid global state in cogs; prefer instance attributes and injected dependencies.
- **Events**
  - Register listeners via `@commands.Cog.listener()` inside cogs.
  - Keep heavy event processing out of listeners; hand off to services or background tasks.

---

## Configuration & Secrets
- Read configuration via a **single `settings`/`config` object**.
- Secrets:
  - Must never be logged, echoed, or written to disk.
  - Must not appear in code, sample files, or tests.
  - For local development, put secrets in a root `.env` file (do not commit `.env`), and use `.env.example` as the non-secret template.
- When adding new configuration:
  - Document the expected env var name and default behavior.
  - Prefer **explicit failure** (e.g. missing required env var) over silently falling back.

---

## Logging & Observability
- Use the standard `logging` module, configured in `logging_config.py`.
- Log levels:
  - `INFO` – startup, shutdown, key lifecycle events.
  - `WARNING` – recoverable problems or suspicious conditions.
  - `ERROR` – failures in commands/services.
  - `DEBUG` – detailed troubleshooting information (safe to disable in production).
- For each command or important action, log:
  - Who invoked it, in which guild/channel, and with what parameters (excluding secrets).
  - Whether it succeeded or failed (and why).
- Do not log entire Discord payloads or huge objects unless strictly necessary.

---

## Testing & Quality
- Prefer **service‑level unit tests** over trying to fully simulate Discord.
- Use `pytest` (and `pytest-asyncio` or similar) for async components.
- Test guidelines:
  - Pure logic functions must have tests.
  - Services with complex behavior must have tests for success and failure paths.
  - At least basic smoke tests for bot startup and extension loading.
- Avoid merging features without at least minimal tests where they provide real value.

---

## Performance & Reliability
- Design commands with the assumption that they may be called frequently:
  - Avoid N+1 queries or repeated heavy computations.
  - Cache where appropriate, with clear invalidation rules.
- Respect Discord’s rate limits:
  - Use built‑in rate limiting tools (cooldowns) and avoid unnecessary API calls.
  - For batch operations, implement small delays and fail‑safes.
- Ensure graceful shutdown:
  - Close open connections (DB, HTTP).
  - Let the bot log a clear shutdown message.

---

## AI Agent Guidelines
When AI tools (like this assistant) modify or add code in this repo, they MUST:

- **Follow this AGENTS.md** as the source of truth for style and architecture decisions.
- Prefer:
  - New cogs/services over overloading large modules.
  - Delegating logic to services instead of cogs.
  - Small, composable functions over large, monolithic ones.
- Avoid:
  - Introducing blocking I/O in async paths.
  - Adding secrets, sample tokens, or credentials anywhere in the repo.
  - Large, unreviewed refactors that change behavior across many modules at once.
- When introducing new patterns or dependencies:
  - Explain the rationale briefly in PR descriptions or commit messages (for humans).
  - Ensure they align with the existing architecture and do not duplicate functionality.

---

## When in Doubt
- Prefer **clarity over cleverness**.
- Prefer **composition over inheritance** (beyond discord.py’s required base classes).
- Keep changes **small, focused, and reversible**.
- If a decision could significantly impact performance, security, or maintainability, document it briefly in the code (non‑obvious reasoning) or in project notes.

