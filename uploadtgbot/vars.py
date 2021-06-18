from os import environ, getcwd


def load_var(var_name, def_value=None):
    return environ.get(var_name, def_value)


class Vars:
    CACHE_TIME = int(load_var("CACHE_TIME", 5))
    DOWN_PATH = f"{getcwd()}/uploadtgbot/downloads"
    BOT_TOKEN = load_var("BOT_TOKEN")
    APP_ID = int(load_var("API_ID"))
    API_HASH = load_var("API_HASH")
    MESSAGE_DUMP = int(load_var("MESSAGE_DUMP", "-100"))
    PREFIX_HANDLER = load_var("PREFIX_HANDLER", "/ !").split()
    SUPPORT_GROUP = load_var("SUPPORT_GROUP", "DivideProjectsDiscussion")
    AUTH_CHANNEL = load_var("AUTH_CHANNEL", -1001218203939)
    OWNER_ID = int(load_var("OWNER_ID", 1198820588))
    DB_URI = load_var("DB_URI")
    CAPTION = load_var("CAPTION", "By @DivideProjects")
    VERSION = load_var("VERSION", "v1.1 - Stable")
    BOT_USERNAME = load_var("BOT_USERNAME")
    WORKERS = load_var("WORKERS", 8)
