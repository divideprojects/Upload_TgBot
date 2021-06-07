from os import environ


def load_var(var_name, def_value=None):
    return environ.get(var_name, def_value)


class Config:
    BOT_TOKEN = load_var("BOT_TOKEN", "1895244956:AAEKEDPvg_8y6kvWVsPZu_X5AhKlg0UhxO0")
    APP_ID = int(load_var("API_ID", 1629442))
    API_HASH = load_var("API_HASH", "6d51f911b14837d4522be8f486841421")
    MESSAGE_DUMP = int(load_var("MESSAGE_DUMP", "-1001433360920"))
    PREFIX_HANDLER = load_var("PREFIX_HANDLER", "/ !").split()
    SUPPORT_GROUP = load_var("SUPPORT_GROUP", "DivideProjectsDiscussion")
    AUTH_CHANNEL = load_var("AUTH_CHANNEL", -1001218203939)
    OWNER_ID = int(load_var("OWNER_ID", 1198820588))
    CAPTION = load_var("CAPTION", "By @DivideProjects")
    VERSION = load_var("VERSION", "v1.1 - Stable")
