import os
import re
import pytz
import asyncio
import datetime

from pyrogram import Client
from pyrogram.errors import FloodWait

# ------------------- CLIENT -------------------

app = Client(
    name="piyush",
    api_id=int(os.environ["API_ID", "39679517"]),
    api_hash=os.environ["API_HASH", "aed61e5ff8c711895f8b0c99e51c16cc"],
    session_string=os.environ["SESSION_STRING", ""],
)

# ------------------- ENV -------------------

TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Kolkata")

BOT_LIST = [
    "Roohi_queen_bot",
    "roshni_x_music_bot",
    "flex_musicbot",
    "gojo_x_jinwoo_bot",
    "snowy_x_musicbot",
]

BOT_ADMIN_IDS = [
    8409591285, 
    7651303468,
    7487670897,
    # replace with your real Telegram user ID
]

CHANNEL_ID = int(os.environ["-1003132769250"])   # Status channel/group
MESSAGE_ID = int(os.environ["65"])   # Message to edit
GRP_ID = int(os.environ["-1003228624224"])           # Logs group

# ------------------- PLUGINS TO CHECK -------------------

PLUGIN_CHECKS = {
    "start": "/start",
    "help": "/help",
    "ping": "/ping",
    "alive": "/alive",
}

# ------------------- HELPERS -------------------

async def check_plugin(bot_username: str, command: str) -> bool:
    """
    Sends a command and checks if bot replies
    """
    try:
        sent = await app.send_message(bot_username, command)
        await asyncio.sleep(6)

        async for msg in app.get_chat_history(bot_username, limit=1):
            if msg.id != sent.id:
                return True
        return False

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return False

    except Exception:
        return False


async def log_to_group(text: str):
    try:
        await app.send_message(GRP_ID, text, disable_web_page_preview=True)
    except Exception:
        pass

# ------------------- MAIN LOOP -------------------

async def main_piyushchecker():
    async with app:
        while True:
            print("🔍 Checking bots status...")

            channel = await app.get_chat(CHANNEL_ID)

            status_text = (
                f"**✨ <u>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {channel.title}</u>**\n\n"
                f"**<u>💫 ʀᴇᴀʟ ᴛɪᴍᴇ ʙᴏᴛ sᴛᴀᴛᴜs</u>**"
            )

            for bot in BOT_LIST:
                await asyncio.sleep(10)

                try:
                    bot_info = await app.get_users(bot)
                except Exception:
                    continue

                # ---------- BASIC LIFE CHECK ----------
                alive = await check_plugin(bot, "/start")

                if not alive:
                    status_text += (
                        f"\n\n╭⎋ **[{bot_info.first_name}](tg://user?id={bot_info.id})**"
                        f"\n╰⊚ **sᴛᴀᴛᴜs: ᴏғғʟɪɴᴇ ❄**"
                    )

                    await log_to_group(
                        f"💀 **BOT DEAD**\n\n"
                        f"➤ **Bot:** [{bot_info.first_name}](tg://user?id={bot_info.id})\n"
                        f"➤ **Username:** @{bot}"
                    )
                    continue

                # ---------- PLUGIN CHECK ----------
                broken = []

                for name, cmd in PLUGIN_CHECKS.items():
                    ok = await check_plugin(bot, cmd)
                    if not ok:
                        broken.append(name)

                if broken:
                    status_text += (
                        f"\n\n╭⎋ **[{bot_info.first_name}](tg://user?id={bot_info.id})**"
                        f"\n╰⊚ **sᴛᴀᴛᴜs: ⚠️ PARTIAL**"
                    )

                    await log_to_group(
                        f"⚠️ **PLUGIN ERROR**\n\n"
                        f"➤ **Bot:** [{bot_info.first_name}](tg://user?id={bot_info.id})\n"
                        f"➤ **Broken Plugins:** `{', '.join(broken)}`"
                    )
                else:
                    status_text += (
                        f"\n\n╭⎋ **[{bot_info.first_name}](tg://user?id={bot_info.id})**"
                        f"\n╰⊚ **sᴛᴀᴛᴜs: ᴏɴʟɪɴᴇ ✨**"
                    )

                await app.read_chat_history(bot)

            # ---------- FOOTER ----------
            now = datetime.datetime.now(pytz.timezone(TIME_ZONE))
            date = now.strftime("%d %b %Y")
            time = now.strftime("%I:%M %p")

            status_text += (
                f"\n\n➻ **ʟᴀꜱᴛ ᴄʜᴇᴄᴋ**"
                f"\n➻ **ᴅᴀᴛᴇ:** {date}"
                f"\n➻ **ᴛɪᴍᴇ:** {time}"
                f"\n\n<u>๏ ʀᴇғʀᴇsʜᴇs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴇᴠᴇʀʏ 30 ᴍɪɴᴜᴛᴇs</u>"
                f"\n\n<b>๏ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @{channel.username}</b>"
            )

            await app.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=MESSAGE_ID,
                text=status_text,
                disable_web_page_preview=True,
            )

            await asyncio.sleep(1800)  # 30 minutes

# ------------------- RUN -------------------

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main_piyushchecker())
