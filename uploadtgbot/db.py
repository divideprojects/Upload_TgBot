from datetime import date

from pymongo import MongoClient

from uploadtgbot import DB_URI, LOGGER


class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection) -> None:
        self._client = MongoClient(DB_URI)
        self._db = self._client["upload_tgbot"]
        self.collection = self._db[collection]

    # Insert one entry into collection
    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    def find_one(self, query):
        result = self.collection.find_one(query)
        if result:
            return result
        return False

    # Find entries from collection
    def find_all(self, query=None):
        if query is None:
            query = {}
        findall_res = [document for document in self.collection.find(query)]
        return findall_res

    # Count entries from collection
    def count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    # Delete entry/entries from collection
    def delete_one(self, query):
        self.collection.delete_many(query)
        after_delete = self.collection.count_documents({})
        return after_delete

    # Replace one entry in collection
    def replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    def update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    def db_command(self, command):
        return self._db.command(command)

    def close(self):
        return self._client.close()


class UserUsage(MongoDB):

    db_name = "users"

    def __init__(self, user_id: int) -> None:
        super().__init__(UserUsage.db_name)
        self.user_id = user_id
        self.user_info = self.__ensure_in_db()

    def add_success_or_fail(self, yes: bool):
        if yes:
            self.user_info["success"] += 1
        else:
            self.user_info["fail"] += 1
        return self.update({"_id": self.user_id}, self.user_info)

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
            f"\n<b>Usage:</b> {user['usage']}"
            "\n\n<b><i>Downloads:</i></b>"
            f"\n<b>Success:</b> {user['success']}"
            f"\n<b>Fail:</b> {user['fail']}"
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
        total_success = sum([i["success"] for i in all_data])
        total_fail = sum([i["fail"] for i in all_data])
        total_downloads = sum(
            len(
                chat
                for chat in all_data["downloads"]
                if len(all_data["downloads"]) >= 1
            ),
        )
        return (
            "<b><i>Stats</i></b>"
            f"\nTotal Users:{total_users}"
            f"\nTotal Usage: {total_usage}"
            f"\nTotal Downloads: {total_downloads}"
            "\n\n<b><i>Downloads:</i></b>"
            f"\nSuccess: {total_success}"
            f"\nFail: {total_fail}"
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
                "success": 0,
                "fail": 0,
            }
            self.insert_one(new_data)
            LOGGER.info(f"Initialized New User: {self.user_id}")
            return new_data
        return user_data


def __connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")


__connect_first()
