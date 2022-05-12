import shutil
import os

from pyrogram import filters, Client
from pyrogram.types import Message
from Yukki import SUDO_USERS, app
from Yukki.YukkiUtilities.helpers.filters import command


@Client.on_message(command("clean") & filters.user(SUDO_USERS))
async def clear_storage(_, message: Message):
    chat_id = message.chat.id
    dir = "downloads"
    dir1 = "search"
    shutil.rmtree(dir)
    shutil.rmtree(dir1)
    os.mkdir(dir)
    os.mkdir(dir1)
    await app.send_message(chat_id, "✅ Cleaned all temp dir(s)!")
