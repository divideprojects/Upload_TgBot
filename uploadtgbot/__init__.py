from logging import INFO, WARNING, StreamHandler, basicConfig, getLogger
from sys import exit as sysexit
from sys import stdout, version_info
from traceback import format_exc
from time import time

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=INFO,
    handlers=[
        StreamHandler(stdout)
    ],
)

getLogger("pyrogram").setLevel(WARNING)

# setup a logger instance
LOGGER = getLogger(__name__)

# if version < 3.7, stop bot.
if version_info[0] < 3 or version_info[1] < 7:
    LOGGER.error(
        (
            "You MUST have a Python Version of at least 3.7!\n"
            "Multiple features depend on this. Bot quitting."
        )
    )
    sysexit(1)  # Quit the Bot

try:
    from .vars import Config
except Exception as ef:
    LOGGER.error(ef)  # Print Error
    LOGGER.error(format_exc())
    sysexit(1)

LOGGER.info("------------------------")
LOGGER.info("|     Upload_TgBot     |")
LOGGER.info("------------------------")
LOGGER.info(f"Version: {Config.VERSION}")
LOGGER.info(f"Owner: {str(Config.OWNER_ID)}\n")


UPTIME = time()
