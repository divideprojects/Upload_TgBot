from datetime import date

from uploadtgbot import LOGGER
from uploadtgbot.db.mongo import MongoDB


class Users(MongoDB):
    db_name = "users"

    def __init__(self, user_id: int) -> None:
        super().__init__(Users.db_name)
        self.user_id = user_id
        self.user_info = self.__ensure_in_db()

    async def add_download(self, dbytes: int, download: str):
        self.user_info["usage"] += dbytes
        self.user_info["downloads"].append(download)
        return await self.update({"_id": self.user_id}, self.user_info)

    async def get_info(self) -> str:
        user = self.user_info
        return (
            "<b><i>Stats</i></b>"
            f"\n<b>Plan</b> {user['plan']}"
            f"\n<b>Restriction</b> {user['restriction']} seconds"
            f"\n<b>Downloads</b> {len(user['downloads'])}"
            f"\n<b>Usage:</b> {humanbytes(user['usage'])}"
        )

    @staticmethod
    async def change_restriction(user_id: int, time: int):
        collection = MongoDB(Users.db_name)
        user_info = await collection.find_one({"_id": user_id})
        user_info["restriction"] = time
        return await collection.update({"_id": user_id}, user_info)

    @staticmethod
    async def change_plan(user_id: int, plan: str):
        collection = MongoDB(Users.db_name)
        user_info = await collection.find_one({"_id": user_id})
        user_info["plan"] = plan
        return await collection.update({"_id": user_id}, user_info)

    @staticmethod
    async def get_all_users():
        return await MongoDB(Users.db_name).find_all()

    @staticmethod
    async def total_users_count():
        return await MongoDB(Users.db_name).count()

    @staticmethod
    async def delete_user(user_id: int):
        return await MongoDB(Users.db_name).delete_one({"_id": user_id})

    # this needs some fixing
    @staticmethod
    async def get_all_usage() -> str:
        collection = MongoDB(Users.db_name)
        all_data = await collection.find_all()
        total_usage = sum(i["usage"] for i in all_data)
        total_users = collection.count()
        total_downloads = sum(len(i["downloads"]) for i in all_data)
        return (
            "<b><i>Stats</i></b>"
            f"\n<b>Total Users:</b>{total_users}"
            f"\n<b>Total Usage:</b> {humanbytes(total_usage)}"
            f"\n<b>Total Downloads:</b> {total_downloads}"
        )

    def __ensure_in_db(self):
        user_data = self.find_one({"_id": self.user_id})
        if not user_data:
            new_data = {
                "_id": self.user_id,
                "usage": 0,
                "restriction": 300,
                "plan": "free",
                "join_date": date.today().isoformat(),
                "downloads": [],  # list of urls
            }
            self.insert_one(new_data)
            LOGGER.info(f"Initialized New User: {self.user_id}")
            return new_data
        return user_data


def humanbytes(size: int or str):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + "B"
