from re import findall

from pyrogram import filters
from pyrogram.types import Message

from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.utils.direct_dl import DirectDl
from uploadtgbot.utils.joinCheck import joinCheck


@UploadTgBot.on_message(filters.command("direct"))
@joinCheck()
async def direct_link(_, m: Message):
    args = m.text.split()
    if len(args) == 1:
        await m.reply_text("You also need to send a link along with the command!")
    else:
        link = args[1]
        if findall(r"\bhttps?://.*\.\S+", link):
            direct_dl = await DirectDl(link).check_url()
            if direct_dl:
                await m.reply_text(direct_dl)
            else:
                await m.reply_text("No direct download links found!")
        else:
            await m.reply_text("Please sent a valid URL.")
    return
