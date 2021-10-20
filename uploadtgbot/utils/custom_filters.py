from asyncio import sleep

from pyrogram import filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message
from pyromod.helpers import ikb

from uploadtgbot import LOGGER
from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import MainDB
from uploadtgbot.vars import Vars

# -- Constants --  #
NO_JOIN_START_TEXT = """
Hey {},
You must join our channel to verify yourself, this step ensures that real users are using the bot!

Click the button below to join the group and verify yourself!
"""
# -- Constants --  #

DEV_LEVEL = [int(Vars.OWNER_ID)]


async def user_check_filter(_, c: UploadTgBot, m: Message):
    user_id = m.from_user.id

    # Update user in Database
    _ = MainDB(user_id)

    # if user is dev or owner, return true
    if user_id in DEV_LEVEL:
        LOGGER.info("Dev User detected, skipping check")
        return True

    try:
        user_member = await c.get_chat_member(int(Vars.AUTH_CHANNEL), user_id)
        # If user is banned in Channel
        if user_member.status == "kicked":
            await m.reply_text(
                (
                    "Sorry, You are Banned!\n"
                    f"Contact my [Support Group](https://t.me/{Vars.SUPPORT_GROUP}) to know more."
                ),
            )
            return
        if user_member:
            LOGGER.info(f"User {user_id} already a member of chat, passing check!")
            return True

    except UserNotParticipant:
        try:
            invite_link = await c.create_chat_invite_link(int(Vars.AUTH_CHANNEL))
            await m.reply_text(
                NO_JOIN_START_TEXT.format(m.from_user.first_name),
                disable_web_page_preview=True,
                parse_mode="markdown",
                reply_markup=ikb([[("Join Channel", invite_link.invite_link, "url")]]),
            )
        except FloodWait as e:
            await sleep(e.x)
            return False
        return False

    except Exception as ef:
        LOGGER.error(f"Error: {ef}")
        await m.reply_text(
            f"Something went Wrong. Contact my [Support Group](https://t.me/{Vars.SUPPORT_GROUP}).",
            disable_web_page_preview=True,
        )
        return


user_check = filters.create(user_check_filter)
