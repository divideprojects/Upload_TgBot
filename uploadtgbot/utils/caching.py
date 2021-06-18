from threading import RLock
from time import perf_counter, time

from cachetools import TTLCache
from pyrogram.types import CallbackQuery
from pyrogram.types.messages_and_media.message import Message

from uploadtgbot import LOGGER

THREAD_LOCK = RLock()

# users stay cached for 5 minutes
block_time = 5 * 60
USER_CACHE = TTLCache(maxsize=512, ttl=block_time, timer=perf_counter)


async def user_cache_reload(m: Message or CallbackQuery):
    global USER_CACHE
    with THREAD_LOCK:
        user_id = m.from_user.id
        USER_CACHE[user_id] = time()
        LOGGER.info(
            f"Restricting {user_id} for {block_time}s",
        )
        return
