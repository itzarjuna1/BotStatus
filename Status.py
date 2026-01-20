import os
import asyncio
import datetime
import pytz

from pyrogram import Client
from pyrogram.errors import FloodWait

# ================= CLIENT =================

app = Client(
    name="piyush",
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    session_string=os.environ["SESSION_STRING"],
)

# ================= ENV =================

TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Kolkata")

# Space-separated bot usernames
BOT_LIST = [i.strip() for i in os.environ.get("BOT_LIST").split()]

# Space-separated admin user IDs
BOT_ADMIN_IDS = [int(i.strip()) for i in os.environ.get("BOT_ADMIN_IDS").split()]

# Logs group ID (must be joined by string session account)
GRP_ID = int(os.environ["GRP_ID"])

# ================= PLUGINS =================

PLUGIN_CHECKS = {
    "start": "/start",
    "help": "/help",
    "ping": "/ping",
    "alive": "/alive",
}

# ================= HELPERS =================

async def check_plugin(bot_username: str, command: str) -> bool:
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

# ================= MAIN LOOP =================

async def main_piyushchecker():
    async with app:
        while True:
            print("🔍 Checking bots status...")

            status_text = "**💫 REAL-TIME BOT STATUS**\n"

            for bot in BOT_LIST:
                await asyncio.sleep(8)

                try:
                    bot_info = await app.get_users(bot)
                except Exception:
                    continue

                # ---- LIFE CHECK ----
                alive = await check_plugin(bot, "/start")

                if not alive:
                    status_text += (
                        f"\n\n❌ **{bot_info.first_name}**"
                        f"\n➤ Status: **OFFLINE**"
                    )

                    await log_to_group(
                        f"💀 **BOT DEAD**\n\n"
                        f"➤ **Bot:** [{bot_info.first_name}](tg://user?id={bot_info.id})\n"
                        f"➤ **Username:** @{bot}"
                    )
                    continue

                # ---- PLUGIN CHECK ----
                broken = []

                for name, cmd in PLUGIN_CHECKS.items():
                    ok = await check_plugin(bot, cmd)
                    if not ok:
                        broken.append(name)

                if broken:
                    status_text += (
                        f"\n\n⚠️ **{bot_info.first_name}**"
                        f"\n➤ Status: **PARTIAL**"
                        f"\n➤ Broken: `{', '.join(broken)}`"
                    )

                    await log_to_group(
                        f"⚠️ **PLUGIN ISSUE**\n\n"
                        f"➤ **Bot:** [{bot_info.first_name}](tg://user?id={bot_info.id})\n"
                        f"➤ **Broken Plugins:** `{', '.join(broken)}`"
                    )
                else:
                    status_text += (
                        f"\n\n✅ **{bot_info.first_name}**"
                        f"\n➤ Status: **ONLINE**"
                    )

                await app.read_chat_history(bot)

            now = datetime.datetime.now(pytz.timezone(TIME_ZONE))
            status_text += (
                f"\n\n🕒 **Last Check**"
                f"\n📅 `{now.strftime('%d %b %Y')}`"
                f"\n⏰ `{now.strftime('%I:%M %p')}`"
                f"\n\n♻️ Auto refresh every **30 minutes**"
            )

            await log_to_group(status_text)
            await asyncio.sleep(1800)

# ================= RUN =================

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main_piyushchecker())
