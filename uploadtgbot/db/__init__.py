from pickledb import load

from uploadtgbot import LOGGER
from uploadtgbot.db.mongo import MongoDB
from uploadtgbot.db.users import Users

LocalDB = load("local.db", True)


def __connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")


__connect_first()
