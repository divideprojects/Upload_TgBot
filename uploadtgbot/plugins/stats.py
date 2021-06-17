from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, Message

from uploadtgbot import OWNER_ID, PREFIX_HANDLER
from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import Users as db
from uploadtgbot.utils.constants import Constants
from uploadtgbot.utils.custom_filters import user_check


@UploadTgBot.on_message(filters.command("stats", PREFIX_HANDLER) & user_check)
async def stats_bot(_, m: Message):
    stats = (
        db.get_all_usage()
        if m.from_user.id == int(OWNER_ID)
        else db(m.from_user.id).get_info()
    )
    await m.reply_text(
        stats,
        quote=True,
        reply_markup=Constants.refresh_stats(m.from_user.id),
    )
    return


@UploadTgBot.on_callback_query(filters.regex("^refresh_"))
async def refresh_stats(_, q: CallbackQuery):
    stats = (
        db.get_all_usage()
        if q.from_user.id == int(OWNER_ID)
        else db(q.from_user.id).get_info()
    )
    try:
        await q.message.edit_text(
            stats,
            reply_markup=Constants.refresh_stats(q.from_user.id),
        )
    except MessageNotModified:
        pass
    await q.answer()


@UploadTgBot.on_callback_query(filters.regex("^upgrade_acct"))
async def upgrade_acct(_, q: CallbackQuery):
    await q.answer("Not yet supported!", show_alert=True)
