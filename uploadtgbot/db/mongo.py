from motor.motor_asyncio import AsyncIOMotorClient

from uploadtgbot import DB_URI

dbClient = AsyncIOMotorClient(DB_URI)


class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection) -> None:
        self._db = dbClient["upload_tgbot"]
        self.collection = self._db[collection]

    # Insert one entry into collection
    async def insert_one(self, document):
        result = await self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    async def find_one(self, query):
        result = await self.collection.find_one(query)
        if result:
            return result
        return False

    # Find entries from collection
    async def find_all(self, query=None):
        if query is None:
            query = {}
        return [document async for document in self.collection.find(query)]

    # Count entries from collection
    async def count(self, query=None):
        if query is None:
            query = {}
        return await self.collection.count_documents(query)

    # Delete entry/entries from collection
    async def delete_one(self, query):
        await self.collection.delete_many(query)
        return await self.collection.count_documents({})

    # Replace one entry in collection
    async def replace(self, query, new_data):
        old = await self.collection.find_one(query)
        _id = old["_id"]
        await self.collection.replace_one({"_id": _id}, new_data)
        new = await self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    async def update(self, query, update):
        result = await self.collection.update_one(query, {"$set": update})
        new_document = await self.collection.find_one(query)
        return result.modified_count, new_document

    async def db_command(self, command):
        return await self._db.command(command)
