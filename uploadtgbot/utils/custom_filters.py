from asyncio import sleep

from pyrogram import filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message
from pyromod.helpers import ikb

from uploadtgbot import AUTH_CHANNEL, LOGGER, OWNER_ID, SUPPORT_GROUP
from uploadtgbot.bot_class import UploadTgBot

# -- Constants --  #
NO_JOIN_START_TEXT = """
You must be a member of the Channel to use the bot, \
this step ensure that you know about bot status \
and latest updates.
This step is also taken to prevent misuse of bot as \
all users will be logged.
"""
# -- Constants --  #

DEV_LEVEL = [int(OWNER_ID)]


async def user_check_filter(_, c: UploadTgBot, m: Message):
    user_id = m.from_user.id

    # if user is dev or owner, return true
    if user_id in DEV_LEVEL:
        LOGGER.info("Dev User detected, skipping check")
        return True

    invite_link = None
    try:
        invite_link = await c.create_chat_invite_link(int(AUTH_CHANNEL))
    except FloodWait as e:
        await sleep(e.x)
        return

    try:
        user_member = await c.get_chat_member(int(AUTH_CHANNEL), user_id)
        # If user is banned in Channel
        if user_member.status == "kicked":
            await m.reply_text(
                (
                    "Sorry, You are Banned!\n"
                    f"Contact my [Support Group](https://t.me/{SUPPORT_GROUP}) to know more."
                ),
            )
            return
        if user_member:
            LOGGER.info(f"User {user_id} already a member of chat, passing check!")
            return True

    except UserNotParticipant:
        await m.reply_text(
            NO_JOIN_START_TEXT,
            disable_web_page_preview=True,
            parse_mode="markdown",
            reply_markup=ikb([[("Join Channel", invite_link.invite_link, "url")]]),
        )
        return False
    except Exception as ef:
        LOGGER.error(f"Error: {ef}")
        await m.reply_text(
            f"Something went Wrong. Contact my [Support Group](https://t.me/{SUPPORT_GROUP}).",
            disable_web_page_preview=True,
        )
        return


user_check = filters.create(user_check_filter)