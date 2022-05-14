from pyrogram import filters
from pyrogram.types import CallbackQuery

from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import LocalDB


@UploadTgBot.on_callback_query(filters.regex("^cancel_"))
async def cancel_operation(_, q: CallbackQuery):
    user_id = q.from_user.id
    q_answer = ""
    task_type = q.data.split("_")[1]

    if task_type == "up":
        LocalDB.set(f"up_{user_id}", False)
        q_answer = "Cancelled Upload Task!"
    if task_type == "dl":
        LocalDB.set(f"dl_{user_id}", False)
        q_answer = "Cancelled Download Task!"

    await q.answer(q_answer)
