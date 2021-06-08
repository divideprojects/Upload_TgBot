from asyncio import sleep
from datetime import datetime
from math import floor
from os import path
from time import time
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import FilePartTooBig, MessageNotModified
from pyrogram.types import Message
from pySmartDL import SmartDL

from uploadtgbot import DOWN_PATH, LOGGER
from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import UserUsage as db
from uploadtgbot.utils.constants import Constants
from uploadtgbot.utils.custom_filters import user_check
from uploadtgbot.utils.display_progress import humanbytes, progress_for_pyrogram


@UploadTgBot.on_message(filters.regex(r"\bhttps?://.*\.\S+") & user_check)
async def download_files(c: UploadTgBot, m: Message):
    link = m.text
    userdb = db(m.from_user.id)
    sm = await m.reply_text("Please Wait!\nChecking link...", quote=True)
    user_down = f"{DOWN_PATH}/{m.from_user.id}/"
    try:
        start_t = datetime.now()
        custom_file_name = path.basename(link)
        if "|" in link:
            url, custom_file_name = link.split("|")
            url = url.strip()
            custom_file_name = custom_file_name.strip()
        else:
            url = link
        print(url, custom_file_name)
        download_file_path = path.join(user_down, custom_file_name)
        downloader = SmartDL(url, download_file_path, progress_bar=False)
        downloader.start(blocking=False)
        c_time = time()
        while not downloader.isFinished():
            total_length = downloader.filesize if downloader.filesize else None
            if total_length > 2097152000:
                await sm.edit_text(
                    "Cannot download files more than 2 GB because of Telegram restrictions!",
                )
                return
            downloaded = downloader.get_dl_size()
            display_message = ""
            now = time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            speed = downloader.get_speed(human=True)
            progress_str = "**[{}{}]**\n**Progress:** __{}%__".format(
                "".join(["●" for _ in range(floor(percentage / 5))]),
                "".join(["○" for _ in range(20 - floor(percentage / 5))]),
                round(percentage, 2),
            )
            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = (
                    f"__**Trying to download...**__\n"
                    f"**URL:** `{link}`\n"
                    f"**File Name:** `{custom_file_name}`\n"
                    f"{progress_str}\n"
                    f"__{humanbytes(downloaded)} of {humanbytes(total_length)}__\n"
                    f"**Speed:** __{speed}__\n"
                    f"**ETA:** __{estimated_total_time}__"
                )
                if round(diff % 10.00) == 0 and current_message != display_message:
                    await sm.edit(current_message, disable_web_page_preview=True)
                    display_message = current_message
                    await sleep(5)
            except MessageNotModified:  # Don't log error if Message is not modified
                pass
            except Exception as ef:
                LOGGER.error(ef)
                LOGGER.error(format_exc())
        if path.exists(download_file_path):
            end_t = datetime.now()
            ms = (end_t - start_t).seconds
            await sm.edit(
                (
                    f"Downloaded to <code>{download_file_path}</code> in <u>{ms}</u> seconds.\n"
                    f"Download Speed: {humanbytes(round((total_length/ms), 2))}"
                ),
            )
            userdb.add_download(dbytes=total_length, download=link)
            try:
                await c.send_document(
                    m.chat.id,
                    download_file_path,
                    caption="Uploaded by @Upload_TgBot",
                    reply_markup=Constants.SUPPORT_KB,
                    progress=progress_for_pyrogram,
                    progress_args=("**__Trying to upload...__**", sm, time()),
                )
                userdb.add_success_or_fail(True)
                await sm.delete()
            except FilePartTooBig:
                await sm.edit_text("Could not upload file!\nSize too big!")
                return
    except Exception as ef:
        LOGGER.error(ef)
        LOGGER.error(format_exc())
        userdb.add_success_or_fail(False)
        await sm.edit_text(f"Failed Download!\n{format_exc()}")
        return
    return
