import random
from asyncio import sleep
from datetime import timedelta
from os import remove
from secrets import token_hex
from time import time
from traceback import format_exc

from aiofiles import open as aio_open
from pyrogram import filters
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import Message

from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import MainDB
from uploadtgbot.vars import Vars

broadcast_ids = {}


async def send_msg(user_id: int, m: Message):
    try:
        await m.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await sleep(e.x)
        return send_msg(user_id, m)
    except InputUserDeactivated:
        return 400, f"{user_id}: deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id}: blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id}: user id invalid\n"
    except Exception as ef:
        return 500, f"{user_id}:{ef}\n{format_exc()}\n"


@UploadTgBot.on_message(
    filters.private
    & filters.command("broadcast")
    & filters.user(Vars.OWNER_ID)
    & filters.reply,
)
async def broadcast_(_, m: Message):
    all_users = MainDB.get_all_users()
    total_users = MainDB.total_users_count()
    done, failed, success = 0, 0, 0

    broadcast_msg = m.reply_to_message
    if not broadcast_msg:
        await m.reply_text("Please reply to a message to broadcast it!")
        return

    broadcast_id = token_hex(random.randint(1, 10))  # generate a random token
    out = await m.reply_text(
        (
            "Broadcast Started!"
            f"\nTotal Users: {total_users}"
            "\nYou will be notified with log file when all the users are notified."
        )
    )

    start_time = time()

    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success,
    )

    async with aio_open("broadcast.txt", "w") as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user["id"]), m=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            elif sts == 400:
                MainDB.delete_user(user["id"])
            else:
                failed += 1

            done += 1

            broadcast_ids[broadcast_id].update(
                dict(current=done, failed=failed, success=success),
            )

    # clear the broadcast dictionary
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)

    completed_in = timedelta(seconds=int(time() - start_time))

    await sleep(3)
    await out.delete()

    broadcast_string = (
        f"Broadcast completed in <code>{completed_in}</code>"
        f"\n\nTotal Users: {total_users}"
        f"\nDone: {done}"
        f"\nSuccess: {success}"
        f"\nFailed: {failed}."
    )

    if failed == 0:
        # means no failed users
        await m.reply_text(
            broadcast_string,
            quote=True,
        )
    else:
        await m.reply_document(
            document="broadcast.txt",
            caption=broadcast_string,
            quote=True,
        )

    remove("broadcast.txt")
