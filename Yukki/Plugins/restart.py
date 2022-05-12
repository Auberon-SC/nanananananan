import os
import shutil
import asyncio
import subprocess

from pyrogram.types import Message
from pyrogram import filters

from Yukki import app, SUDOERS
from Yukki.YukkiUtilities.database import get_active_video_chats
from Yukki.YukkiUtilities.database.queue import get_active_chats, remove_active_chat


@app.on_message(filters.command("restart") & filters.user(SUDOERS))
async def restart_server(_, message):
    chat_id = message.chat.id
    A = "downloads"
    B = "raw_files"
    shutil.rmtree(A)
    shutil.rmtree(B)
    await asyncio.sleep(2)
    os.mkdir(A)
    os.mkdir(B)
    served_chats = []
    try:
        chats = await get_active_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception:
        pass
    for x in served_chats:
        try:
            await app.send_message(
                x,
                f"Group Music Bot server has just restarted.\n\nSorry for the issues, start playing after 15-20 seconds again.",
            )
            await remove_active_chat(x)
        except Exception:
            pass
    x = await app.send_message(chat_id, f"Restarting group music bot.")
    os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")


@app.on_message(filters.command("update") & filters.user(SUDOERS))
async def update_bot(_, message):
    chat_id = message.chat.id
    m = subprocess.check_output(["git", "pull"]).decode("UTF-8")
    if str(m[0]) != "A":
        await app.send_message(chat_id, "Update found, pushing now !")
        return os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
    else:
        await app.send_message(chat_id, "Bot is already up-to-date")


@app.on_message(filters.command("activevc") & filters.user(SUDOERS))
async def activevc(_, message: Message):
    chat_id = message.chat.id
    served_chats = []
    try:
        chats = await get_active_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception as e:
        await app.send_message(chat_id, f"Error occured: `{e}`")
    text = ""
    j = 0
    for x in served_chats:
        try:
            title = (await app.get_chat(x)).title
        except Exception:
            title = "Private Group"
        if (await app.get_chat(x)).username:
            user = (await app.get_chat(x)).username
            text += f"<b>{j + 1}.</b>  [{title}](https://t.me/{user})[`{x}`]\n"
        else:
            text += f"<b>{j + 1}. {title}</b> [`{x}`]\n"
        j += 1
    if not text:
        await app.send_message(chat_id, "❌ No active voice chats")
    else:
        await app.send_message(
            chat_id,
            f"💡 **Active voice chats:**\n\n{text}",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command("activevideo") & filters.user(SUDOERS))
async def activevi_(_, message: Message):
    chat_id = message.chat.id
    served_chats = []
    try:
        chats = await get_active_video_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception as e:
        await app.send_message(chat_id, f"**Error occured:** `{e}`")
    text = ""
    j = 0
    for x in served_chats:
        try:
            title = (await app.get_chat(x)).title
        except Exception:
            title = "Private Group"
        if (await app.get_chat(x)).username:
            user = (await app.get_chat(x)).username
            text += f"<b>{j + 1}.</b>  [{title}](https://t.me/{user})[`{x}`]\n"
        else:
            text += f"<b>{j + 1}. {title}</b> [`{x}`]\n"
        j += 1
    if not text:
        await app.send_message(chat_id, "No Active Video Calls")
    else:
        await app.send_message(
            chat_id,
            f"**Active Video Calls:-**\n\n{text}",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command("leavebot") & filters.user(SUDOERS))
async def bot_leave_group(_, message):
    chat_id = message.chat.id
    if len(message.command) != 2:
        await app.send_message(
            chat_id, "**Usage:**\n\n/leavebot [chat username or chat id]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        await app.leave_chat(chat)
    except Exception as e:
        await app.send_message(chat_id, f"❌ Procces failed\n\nPosible reason: `{e}`")
        print(e)
        return
    await app.send_message(chat_id, "✅ Bot successfully left chat")
