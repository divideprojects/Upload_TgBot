from pickledb import load
from datetime import datetime
from uploadtgbot import LOGGER
from uploadtgbot.vars import Vars
from uploadtgbot.db.mongo import MongoDB
from time import time

# Local database from pickledb
LocalDB = load(f"{Vars.BOT_USERNAME}_local.db", True)


class MainDB(MongoDB):
    """
    Class to manage collection of bot in MongoDB
    """

    # bot username, which will be used as collection name
    db_name = Vars.BOT_USERNAME

    def __init__(self, user_id: int) -> None:
        """
        initialise the class MainDB by passing a user_id to get user_info
        """
        super().__init__(MainDB.db_name)
        self.user_id = user_id
        self.user_info = self.__ensure_in_db()  # get user_info from database

    def add_download(self, download_url: str, file_size: int, message_id: int):
        """
        Add download to list in user_info
        """
        new_download_data = {
            "url": download_url,
            "file_size": file_size,
            "message_id": message_id,
            "time": time()
        }
        self.user_info["downloads"].append(new_download_data)
        self.update_user_stats()  # update the stats of user
        return self.update({"_id": self.user_id}, self.user_info)

    def update_user_stats(self):
        """
        Update the stats of user by getting values again!
        """
        total_usage = sum(i["file_size"] for i in self.user_info["downloads"])
        self.user_info["total_usage"] = total_usage
        total_downloads = len(self.user_info["downloads"])
        self.user_info["total_downloads"] = total_downloads

    def get_info(self):
        """
        Function used to get info about a certain user
        """
        return self.user_info

    def change_plan(self, plan: str):
        """
        This function is used to change the plan of user
        """
        self.user_info["plan"] = plan
        return self.update({"_id": self.user_id}, self.user_info)

    @staticmethod
    def get_all_users():
        """
        This function is used to get all the users stored in database
        """
        return MongoDB(MainDB.db_name).find_all()

    @staticmethod
    def total_users_count():
        """
        This function is used to count all the users stored in database
        """
        return MongoDB(MainDB.db_name).count()

    @staticmethod
    def delete_user(user_id: int):
        """
        This function deletes the user from database
        """
        return MongoDB(MainDB.db_name).delete_one({"_id": user_id})

    @staticmethod
    def get_all_usage():
        """
        This function gets all the data about all the users
        """
        collection = MongoDB(MainDB.db_name)
        all_data = collection.find_all()
        LOGGER.info(all_data)
        total_usage = sum(i["downloads"]["usage"] for i in all_data)
        total_users = collection.count()
        total_downloads = sum(len(i["downloads"]) for i in all_data)
        return total_usage, total_users, total_downloads

    def __ensure_in_db(self):
        """
        This function ensures that the user is already in db and fixes data to latest schema
        """
        user_data = self.find_one({"_id": self.user_id})
        if not user_data:
            new_data = {
                "_id": self.user_id,  # user id of user
                "total_usage": 0,  # usage of user in bytes
                "total_downloads": 0,  # total downloads by user in bytes
                "plan": "free",  # Plan of use
                "join_date": datetime.now().isoformat(),  # Joining date of user with time
                "downloads": [],  # list[dictionary{}] with data specific for each URL
            }
            self.insert_one(new_data)
            LOGGER.info(f"Initialized New User: {self.user_id}")
            return new_data
        return user_data


def __connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")


__connect_first()
