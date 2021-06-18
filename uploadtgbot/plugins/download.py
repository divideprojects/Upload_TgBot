from asyncio import sleep
from datetime import datetime
from datetime import timedelta
from math import floor
from os import path, remove
from re import findall
from time import time
from traceback import format_exc

from httpx import get, RequestError
from pySmartDL import SmartDL
from pyrogram import filters
from pyrogram.errors import FilePartTooBig, MessageNotModified
from pyrogram.types import Message
from pyromod.helpers import ikb

from uploadtgbot import LOGGER
from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import LocalDB
from uploadtgbot.db import MainDB
from uploadtgbot.utils.caching import user_cache_reload, user_cache_check
from uploadtgbot.utils.constants import Constants
from uploadtgbot.utils.custom_filters import user_check
from uploadtgbot.utils.display_progress import (
    human_bytes,
    progress_for_pyrogram,
)
from uploadtgbot.vars import Vars


async def get_custom_filename(link: str):
    if "|" in link:
        url, file_name = link.split("|")
        url = url.strip()
        file_name = file_name.strip()
    else:
        url = link
        try:
            cd = get(url).headers.get('content-disposition')
            file_name = findall("filename=(.+)", cd)

            if len(file_name) == 0:
                return url, path.basename(link)

            return file_name[0]
        except Exception as ef:
            LOGGER.error(ef)
            LOGGER.error(format_exc())

            file_name = path.basename(link)
    return url, file_name


@UploadTgBot.on_message(filters.regex(r"\bhttps?://.*\.\S+") & user_check)
async def download_files(c: UploadTgBot, m: Message):
    user_id = m.from_user.id
    link = m.text

    cache_status, cache_time = await user_cache_check(m)

    if cache_status:
        await m.reply_text(
            "Spam protection active!\n"
            f"Please try again after {timedelta(seconds=cache_time)} seconds",
        )
        return

    LocalDB.set(f"dl_{user_id}", True)
    user_db = MainDB(user_id)
    sm = await m.reply_text("Please Wait!\nChecking link...", quote=True)
    user_down = f"{Vars.DOWN_PATH}/{user_id}/"
    start_t = datetime.now()

    try:
        url, custom_file_name = await get_custom_filename(link)
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

            total_length = downloader.filesize or 0
            downloaded = downloader.get_dl_size()

            if (downloaded or total_length) > 2097152000:  # size less than 2gb
                await sm.edit_text(
                    "Cannot download files more than 2 GB because of Telegram restrictions!"
                )
                return

            display_message = ""
            diff = time() - c_time
            percentage = downloader.get_progress() * 100
            speed = downloader.get_speed(human=True)
            progress_str = "<b>[{}{}]</b>\n<b>Progress:</b> <i>{}%</i>".format(
                "".join("●" for _ in range(floor(percentage / 5))),
                "".join("○" for _ in range(20 - floor(percentage / 5))),
                round(percentage, 2),
            )

            # get download eta
            estimated_total_time = downloader.get_eta(human=True)

            try:
                current_message = (
                    f"<i><b>Trying to download...</b></i>\n"
                    f"<b>URL:</b> <i>{url}</i>\n"
                    f"<b>File Name:</b> <i>{custom_file_name}</i>\n"
                    f"<i>{progress_str}</i>\n"
                    f"<i>{human_bytes(downloaded)} of {human_bytes(total_length)}</i>\n"
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
                    f"Download Speed: {human_bytes(round((total_length / ms), 2))}"
                )
            )

            LocalDB.set(f"up_{user_id}", True)
            # Log download to database
            user_db.add_download(download_url=url, file_size=total_length, message_id=m.message_id)

            try:
                file_size = path.getsize(download_file_path)
                caption = (
                    f"<b>File Name:</b> <i>{custom_file_name}</i>"
                    f"\n<b>File Size</b> <i>{human_bytes(file_size)}</i>"
                    f"\n<b>URL:</b> {url}"
                    "\n\nUploaded by @Upload_TgBot"
                )
                await c.send_document(
                    user_id,
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
                await sm.edit_text(
                    (
                        "Could not upload file!"
                        "\nSize too big! (Larger than 2GB)"
                    )
                )
                return

    except Exception as ef:
        LOGGER.error(ef)
        LOGGER.error(format_exc())
        await sm.edit_text(f"Failed Download!\n{format_exc()}")
        return

    remove(download_file_path)
    return
