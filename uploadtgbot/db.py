from datetime import date

from pickledb import load
from pymongo import MongoClient

from uploadtgbot import DB_URI, LOGGER

LocalDB = load("local.db", True)
dbClient = MongoClient(DB_URI)


class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection) -> None:
        self._db = dbClient["upload_tgbot"]
        self.collection = self._db[collection]

    # Insert one entry into collection
    def __insert_one(self, document):
        result = self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    def __find_one(self, query):
        result = self.collection.find_one(query)
        if result:
            return result
        return False

    # Find entries from collection
    def __find_all(self, query=None):
        if query is None:
            query = {}
        findall_res = [document for document in self.collection.find(query)]
        return findall_res

    # Count entries from collection
    def __count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    # Delete entry/entries from collection
    def __delete_one(self, query):
        self.collection.delete_many(query)
        after_delete = self.collection.count_documents({})
        return after_delete

    # Replace one entry in collection
    def __replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    def __update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    def __db_command(self, command):
        return self._db.command(command)

    def __close(self):
        return self._client.close()


class UserUsage(MongoDB):

    db_name = "users"

    def __init__(self, user_id: int) -> None:
        super().__init__(UserUsage.db_name)
        self.user_id = user_id
        self.user_info = self.__ensure_in_db()

    def add_download(self, dbytes: int, download: str):
        self.user_info["usage"] += dbytes
        self.user_info["downloads"].append(download)
        return self.update({"_id": self.user_id}, self.user_info)

    def get_info(self) -> str:
        user = self.user_info
        return (
            "<b><i>Stats</i></b>"
            f"\n<b>Plan</b> {user['plan']}"
            f"\n<b>Restriction</b> {user['restriction']} seconds"
            f"\n<b>Downloads</b> {len(user['downloads'])}"
            f"\n<b>Usage:</b> {humanbytes(user['usage'])}"
        )

    @staticmethod
    def change_restriction(user_id: int, time: int):
        collection = MongoDB(UserUsage.db_name)
        user_info = collection.find_one({"_id": user_id})
        user_info["restriction"] = time
        return collection.update({"_id": user_id}, user_info)

    @staticmethod
    def change_plan(user_id: int, plan: str):
        collection = MongoDB(UserUsage.db_name)
        user_info = collection.find_one({"_id": user_id})
        user_info["plan"] = plan
        return collection.update({"_id": user_id}, user_info)

    # this needs some fixing
    @staticmethod
    def get_all_usage() -> str:
        collection = MongoDB(UserUsage.db_name)
        all_data = collection.find_all()
        total_usage = sum([i["usage"] for i in all_data])
        total_users = collection.count()
        total_downloads = 0
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


def __connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")


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


__connect_first()
