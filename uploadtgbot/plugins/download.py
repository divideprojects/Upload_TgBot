from asyncio import sleep
from datetime import datetime
from math import floor
from os import path, remove
from time import time
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import FilePartTooBig, MessageNotModified
from pyrogram.types import Message
from pyromod.helpers import ikb
from pySmartDL import SmartDL

from uploadtgbot import DOWN_PATH, LOGGER, OWNER_ID
from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import LocalDB
from uploadtgbot.db import UserUsage as db
from uploadtgbot.utils.caching import USER_CACHE, block_time, user_cache_reload
from uploadtgbot.utils.constants import Constants
from uploadtgbot.utils.custom_filters import user_check
from uploadtgbot.utils.display_progress import (
    TimeFormatter,
    humanbytes,
    progress_for_pyrogram,
)


@UploadTgBot.on_message(filters.regex(r"\bhttps?://.*\.\S+") & user_check)
async def download_files(c: UploadTgBot, m: Message):
    user_id = m.from_user.id
    if m.from_user.id != OWNER_ID and m.from_user.id in set(list(USER_CACHE.keys())):
        await m.reply_text(
            "Spam protection active!\n"
            f"Please try again after {TimeFormatter((((USER_CACHE[m.from_user.id]+block_time)-time())*1000))} minutes",
        )
        return

    link = m.text
    LocalDB.set(f"dl_{user_id}", True)
    userdb = db(user_id)
    sm = await m.reply_text("Please Wait!\nChecking link...", quote=True)
    user_down = f"{DOWN_PATH}/{user_id}/"
    try:
        start_t = datetime.now()
        custom_file_name = path.basename(link)
        if "|" in link:
            url, custom_file_name = link.split("|")
            url = url.strip()
            custom_file_name = custom_file_name.strip()
        else:
            url = link
        download_file_path = path.join(user_down, custom_file_name)
        downloader = SmartDL(url, download_file_path, progress_bar=False)
        downloader.start(blocking=False)
        await user_cache_reload(m)
        c_time = time()
        while not downloader.isFinished():
            # Cancel the download task
            if not LocalDB.get(f"dl_{user_id}"):
                downloader.stop()
                await sm.edit_text("Task Cancelled by User!")
                return
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
            progress_str = "<b>[{}{}]</b>\n<b>Progress:</b> <i>{}%</i>".format(
                "".join(["●" for _ in range(floor(percentage / 5))]),
                "".join(["○" for _ in range(20 - floor(percentage / 5))]),
                round(percentage, 2),
            )
            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = (
                    f"<i><b>Trying to download...</b></i>\n"
                    f"<b>URL:</b> <i>{url}</i>\n"
                    f"<b>File Name:</b> <i>{custom_file_name}</i>\n"
                    f"<i>{progress_str}</i>\n"
                    f"<i>{humanbytes(downloaded)} of {humanbytes(total_length)}</i>\n"
                    f"<b>Speed:</b> <i>{speed}</i>\n"
                    f"<b>ETA:</b> <i>{estimated_total_time}</i>"
                )
                if round(diff % 10.00) == 0 and current_message != display_message:
                    # Cancel the Download process
                    if not LocalDB.get(f"dl_{user_id}"):
                        await sm.edit_text("Download task cancelled by user!")
                        return
                    await sm.edit_text(
                        current_message,
                        reply_markup=ikb([[("Cancel ❌", "cancel_dl")]]),
                        disable_web_page_preview=True,
                    )
                    display_message = current_message
                    await sleep(2)
            except MessageNotModified:  # Don't log error if Message is not modified
                pass
            except Exception as ef:
                LOGGER.error(ef)
                LOGGER.error(format_exc())
        if path.exists(download_file_path):
            end_t = datetime.now()
            ms = (end_t - start_t).seconds
            await sm.edit_text(
                (
                    f"Downloaded to file in <u>{ms}</u> seconds.\n"
                    f"Download Speed: {humanbytes(round((total_length/ms), 2))}"
                ),
            )
            LocalDB.set(f"up_{user_id}", True)
            userdb.add_download(dbytes=total_length, download=link)
            try:
                file_size = path.getsize(download_file_path)
                caption = (
                    f"<b>File Name:</b> <i>{custom_file_name}</i>"
                    f"\n<b>File Size</b> <i>{humanbytes(file_size)}</i>"
                    f"\n<b>URL:</b> {url}"
                    "\n\nUploaded by @Upload_TgBot"
                )
                await c.send_document(
                    m.chat.id,
                    download_file_path,
                    caption=caption,
                    reply_markup=Constants.SUPPORT_KB,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "**__Trying to upload...__**",
                        sm,
                        time(),
                        user_id,
                        c,
                    ),
                )
                await sm.delete()
            except FilePartTooBig:
                await sm.edit_text("Could not upload file!\nSize too big!")
                return
    except Exception as ef:
        LOGGER.error(ef)
        LOGGER.error(format_exc())
        await sm.edit_text(f"Failed Download!\n{format_exc()}")
        return
    remove(download_file_path)
    return
