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

