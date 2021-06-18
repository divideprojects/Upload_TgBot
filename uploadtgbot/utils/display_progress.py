from asyncio import sleep
from math import floor
from time import time
from traceback import format_exc

from pyrogram.errors import MessageNotModified
from pyromod.helpers import ikb

from uploadtgbot import LOGGER
from uploadtgbot.db import LocalDB
from uploadtgbot.utils.constants import Constants


async def progress_for_pyrogram(
        current,
        total,
        ud_type,
        message,
        start,
        user_id,
        client,
):
    if not LocalDB.get(f"up_{user_id}"):
        await message.reply_text("Cancelled Upload Task!")
        await client.stop_transmission()
        return
    now = time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        estimated_total_time = time_formatter(milliseconds=estimated_total_time)

        progress = "[{}{}] \n".format(
            "".join("●" for _ in range(floor(percentage / 5))),
            "".join("○" for _ in range(20 - floor(percentage / 5))),
        )

        tmp = progress + Constants.PROGRESS.format(
            round(percentage, 2),
            human_bytes(current),
            human_bytes(total),
            human_bytes(speed),
            estimated_total_time if estimated_total_time != "" else "0 s",
        )
        try:
            # Cancel the upload process
            await message.edit_text(
                text=f"<b>{ud_type}</b>\n\n{tmp}",
                reply_markup=ikb([[("Cancel ❌", f"cancel_up")]]),
            )
        except MessageNotModified:
            await sleep(2)
        except Exception as ef:
            LOGGER.error(ef)
            LOGGER.error(format_exc())


def human_bytes(size: int or str):
    if not size:
        return "0B"
    power = 2 ** 10
    n = 0
    dic_power_n = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + dic_power_n[n] + "B"


def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
            ((str(days) + "d, ") if days else "")
            + ((str(hours) + "h, ") if hours else "")
            + ((str(minutes) + "m, ") if minutes else "")
            + ((str(seconds) + "s, ") if seconds else "")
            + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]
