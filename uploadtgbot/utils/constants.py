from pyromod.helpers import ikb

from uploadtgbot import CAPTION, OWNER_ID, SUPPORT_GROUP


class Constants:
    def refresh_stats(user_id: int):
        return ikb(
            [[("Upgrade 💰", "upgrade_acct"), ("Refresh 🔄", f"refresh_{user_id}")]],
        )

    START_KB = [
        [
            ("How to use", "help_callback.start"),
            ("Help & Support", f"https://t.me/{SUPPORT_GROUP}", "url"),
        ],
    ]
    page1_help_kb = [[(">>>", "help_callback.page2")]]
    page2_help_kb = [[("<<<", "help_callback.page1"), (">>>", "help_callback.page3")]]
    page3_help_kb = [[("<<<", "help_callback.page2")]]

    SUPPORT_KB = ikb(
        [
            [
                ("Support Group", f"https://t.me/{SUPPORT_GROUP}", "url"),
                ("Bots Channel", "https://t.me/DivideProjects", "url"),
            ],
        ],
    )

    @staticmethod
    def ban_kb(user_id: int):
        return ikb([[("Ban User", f"ban_{user_id}")]]) if user_id != OWNER_ID else None

    USAGE_WATERMARK_ADDER = f"""
Hi {{}}, I am Telegram File Uploader Bot!

I can download files from a URL, just me a link to see what I can do!
{CAPTION}
"""

    page1_help = """
<b><u>Commands:</b></u>
/start: <i>Start the bot.</i>
/help: <i>Show this message.</i>
/direct (url here): <i>Give you the direct links of supported urls</i>
/stats: <i>Get your current Stats</i>
-> Check next page for more details

Just send me a direct download link and I will send the file to you!
To download file with a custom name, use this format: <code>link | filename</code>
"""

    page2_help = """
<u><i><b>Supported Links:</b></i></u>
<i>I also support the links from these website other than direct links!</i>
You can get the direct links by using this syntax: <code>/direct (url here)</code>

- <a href='https://mediafire.com'><i>Mediafire</i></a>
- <a href='https://drive.google.com'><i>Google Drive</i></a>
- <a href='https://github.com'><i>Github</i></a>
- <a href='https://disk.yandex.com'><i>Yandex</i></a>
- <a href='https://sourceforge.com'><i>Sourceforge</i></a>
- <a href='https://osdn.net'><i>OSDN</i></a>
"""

    page3_help = f"""
<b><u>FAQs</b></u>:

<b>• Why is bot slow?</b>
- <i>Bot is hosted on free Heroku server, which ultimately makes it slow.</i>

<b>• Is NSFW allowed on Bot?</b>
- <i>No, any user found uploading and using NSFW Videos on Bot will be banned infinitely.</i>

<b>• Will the bot support more Direct links in future?</b>
- <i>Yes, I will as much features as possible, if you want a specific feature, make it and send to @{SUPPORT_GROUP}</i>

<b>• Why is there a restriction of 5 minutes?</b>
- <i>For now bot is providing every service for free and that could be misused by spammers so in restriction is there in order to maintain a stable performance all of the users.</i>
"""

    PROGRESS = """
<b>Percentage:</b> <i>{0}%</i>
<b>✅ Done:</b> <i>{1}</i>
<b>🌀 Total:</b> <i>{2}</i>
<b>🚀 Speed:</b> <i>{3}/s</i>
<b>🕰 ETA:</b> <i>{4}</i>
"""
