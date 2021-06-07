from pyrogram import filters
from pyrogram.types import Message

from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.utils.custom_filters import user_check
from uploadtgbot.utils.direct_dl import DirectDl


@UploadTgBot.on_message(filters.command("direct") & user_check)
async def direct_link(_, m: Message):
    args = m.tetx.split()
    if len(args) == 1:
        await m.reply_text("You also need to send a link along with the command!")
    else:
        link = args[1]
        direct_dl = DirectDl(link).check_url()
        if direct_dl:
            await m.reply_text(direct_dl)
    return