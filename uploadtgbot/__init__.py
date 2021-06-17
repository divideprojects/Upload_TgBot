from datetime import datetime
from logging import INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger
from os import environ, getcwd, mkdir, path
from sys import exit as sysexit
from sys import stdout, version_info
from time import time
from traceback import format_exc

LOG_DATETIME = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
LOGDIR = f"{__name__}/logs"

# Make Logs directory if it does not exists
if not path.isdir(LOGDIR):
    mkdir(LOGDIR)

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=INFO,
    handlers=[
        FileHandler(filename=f"{LOGDIR}/{__name__}_{LOG_DATETIME}.log"),
        StreamHandler(stdout),
    ],
)

getLogger("pyrogram").setLevel(WARNING)
LOGGER = getLogger(__name__)

# if version < 3.9, stop bot.
if version_info[0] < 3 or version_info[1] < 7:
    LOGGER.error(
        (
            "You MUST have a Python Version of at least 3.7!\n"
            "Multiple features depend on this. Bot quitting."
        ),
    )
    sysexit(1)  # Quit the Script

# the secret configuration specific things
try:
    if environ.get("ENV", "ANYTHING"):
        from .vars import Config
    else:
        from .local_vars import Development as Config
except Exception as ef:
    LOGGER.error(ef)  # Print Error
    LOGGER.error(format_exc())
    sysexit(1)

LOGGER.info("------------------------")
LOGGER.info("|     Upload_TgBot     |")
LOGGER.info("------------------------")
LOGGER.info(f"Version: {Config.VERSION}")
LOGGER.info(f"Owner: {str(Config.OWNER_ID)}\n")

# Account Related
BOT_TOKEN = Config.BOT_TOKEN
APP_ID = Config.APP_ID
API_HASH = Config.API_HASH
MESSAGE_DUMP = Config.MESSAGE_DUMP
PREFIX_HANDLER = Config.PREFIX_HANDLER
SUPPORT_GROUP = Config.SUPPORT_GROUP
AUTH_CHANNEL = Config.AUTH_CHANNEL
CAPTION = Config.CAPTION
OWNER_ID = Config.OWNER_ID
VERSION = Config.VERSION
DB_URI = Config.DB_URI
DOWN_PATH = f"{getcwd()}/uploadtgbot/downloads"
UPTIME = time()  # Check bot uptime
