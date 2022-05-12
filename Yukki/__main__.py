import asyncio

from platform import python_version as kontol
from pytgcalls import idle, __version__ as memek
from pyrogram import Client, __version__ as kntl
from Yukki import BOT_NAME, ASSNAME, app, chacha
from Yukki.config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    LOG_GROUP_ID,
    LOG_GROUP_ID_2,
    AUTO_LEAVE,
)
from Yukki.YukkiUtilities.database.functions import clean_restart_stage
from Yukki.YukkiUtilities.database.queue import get_active_chats, remove_active_chat
from Yukki.YukkiUtilities.tgcallsrun import run


Client(
    ":groupmusic:",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "Yukki.Plugins"},
).start()


print(f"[ INFO ] : BOT STARTED AS {BOT_NAME}!")
print(f"[ INFO ] : ASSISTANT STARTED AS {ASSNAME}!")


async def load_start():
    restart_data = await clean_restart_stage()
    if restart_data:
        print("[ INFO ] : SENDING RESTART STATUS")
        try:
            await app.edit_message_text(
                restart_data["chat_id"],
                restart_data["message_id"],
                "✅ **Bot restarted successfully.**",
            )
        except Exception:
            pass
    served_chats = []
    try:
        chats = await get_active_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception:
        print("Error came while clearing db")
    for served_chat in served_chats:
        try:
            await remove_active_chat(served_chat)
        except Exception:
            print("Error came while clearing db")
            pass
    await app.send_message(
        LOG_GROUP_ID,
        f"Resso Stream Started:\n\nPython: `{kontol()}`\nPyrogram: `{kntl}`\nPyTgcalls: `{memek.__version__}`",
    )
    await chacha.send_message(LOG_GROUP_ID_2, "Assistant Started")
    print("[ INFO ] : GROUP MUSIC CLIENT STARTED")


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(load_start())
run()
idle()

loop.close()
print("[INFO]: BOT & USERBOT STOPPED")
