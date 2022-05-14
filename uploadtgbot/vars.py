from os import getcwd

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])


class Vars:
    CACHE_TIME = int(config("CACHE_TIME", default=5))
    DOWN_PATH = f"{getcwd()}/uploadtgbot/downloads"
    BOT_TOKEN = config("BOT_TOKEN")
    APP_ID = int(config("API_ID"))
    API_HASH = config("API_HASH")
    MESSAGE_DUMP = int(config("MESSAGE_DUMP", default=-100))
    PREFIX_HANDLER = config("PREFIX_HANDLER", default="/ !").split()
    SUPPORT_GROUP = config("SUPPORT_GROUP", default="DivideProjectsDiscussion")
    AUTH_CHANNEL = config("AUTH_CHANNEL", default=-1001218203939)
    OWNER_ID = int(config("OWNER_ID", default=1198820588))
    DB_URI = config("DB_URI")
    CAPTION = config("CAPTION", default="By @DivideProjects")
    VERSION = config("VERSION", default="v1.1 - Stable")
    BOT_USERNAME = config("BOT_USERNAME")
    WORKERS = config("WORKERS", default=8)
    JOIN_CHECK = config("JOIN_CHECK", default=None, cast=config.boolean)
