from pyrogram import filters
from pyrogram.types import CallbackQuery, Message
from pyromod.helpers import ikb

from uploadtgbot import PREFIX_HANDLER
from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import UserUsage as db
from uploadtgbot.utils.constants import Constants
from uploadtgbot.utils.custom_filters import user_check


@UploadTgBot.on_message(
    filters.command("start", PREFIX_HANDLER) & filters.private & user_check,
)
async def start_bot(_, m: Message):
    _ = db(m.from_user.id)
    await m.reply_text(
        Constants.USAGE_WATERMARK_ADDER.format(m.from_user.first_name),
        reply_markup=ikb(Constants.START_KB),
        disable_web_page_preview=True,
        quote=True,
    )


@UploadTgBot.on_message(
    filters.command("help", PREFIX_HANDLER) & filters.private & user_check,
)
async def help_bot(_, m: Message):
    _ = db(m.from_user.id)
    await m.reply_text(
        Constants.page1_help,
        reply_markup=ikb(Constants.page1_help_kb),
        disable_web_page_preview=True,
    )


@UploadTgBot.on_callback_query(filters.regex("^help_callback."))
async def help_callback_func(_, q: CallbackQuery):
    qdata = q.data.split(".")[1]
    if qdata in ("start", "page1"):
        await q.message.edit_text(
            Constants.page1_help,
            reply_markup=ikb(Constants.page1_help_kb),
            disable_web_page_preview=True,
        )
    elif qdata == "page2":
        await q.message.edit_text(
            Constants.page2_help,
            reply_markup=ikb(Constants.page2_help_kb),
            disable_web_page_preview=True,
        )
    elif qdata == "page3":
        await q.message.edit_text(
            Constants.page3_help,
            reply_markup=ikb(Constants.page3_help_kb),
            disable_web_page_preview=True,
        )
    await q.answer()
