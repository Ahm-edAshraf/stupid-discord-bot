import logging
import sys


def setup_logging() -> None:
    """Configure root logging for the bot."""
    root = logging.getLogger()
    if root.handlers:
        # Avoid duplicate handlers when reloading in development.
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root.setLevel(logging.INFO)
    root.addHandler(handler)

    # This template uses application commands (slash commands) only.
    # discord.py's commands extension can still emit a warning about the
    # privileged `message_content` intent even though prefix commands aren't
    # used. Hide that noise but keep real errors visible.
    logging.getLogger("discord.ext.commands.bot").setLevel(logging.ERROR)

