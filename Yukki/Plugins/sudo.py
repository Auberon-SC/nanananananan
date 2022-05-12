import os

from inspect import getfullargspec
from Yukki import app, OWNER
from Yukki.YukkiUtilities.database.sudo import (
    get_sudoers,
    get_sudoers,
    remove_sudo,
    add_sudo,
)
from pyrogram import filters
from pyrogram.types import Message


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(filters.command("addsudo") & filters.user(OWNER))
async def useradd(_, message: Message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        if len(message.command) != 2:
            await app.send_message(
                chat_id, "Reply to a user's message or give username/user_id"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        sudoers = await get_sudoers()
        if user.id in sudoers:
            return await app.send_message(chat_id, "✅ Already a **sudo user**")
        added = await add_sudo(user.id)
        if added:
            await app.send_message(
                chat_id, f"✅ Added **{user.mention}** to sudo user list !"
            )
            return os.execvp("python3", ["python3", "-m", "Yukki"])
        await edit_or_reply(message, text="Something wrong happened, check logs.")
        return
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id in sudoers:
        return await app.send_message(chat_id, "✅ Already a sudo user")
    added = await add_sudo(user_id)
    if added:
        await app.send_message(chat_id, f"✅ Added {mention} sudo user list !")
        return os.execvp("python3", ["python3", "-m", "Yukki"])
    await edit_or_reply(message, text="Something wrong happened, check logs.")
    return


@app.on_message(filters.command("delsudo") & filters.user(OWNER))
async def userdel(_, message: Message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        if len(message.command) != 2:
            await app.send_message(
                chat_id, "Reply to a user's message or give username/user id."
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id not in await get_sudoers():
            return await app.send_message(
                chat_id, f"❌ User is not a part of group music bot"
            )
        removed = await remove_sudo(user.id)
        if removed:
            await app.send_message(
                chat_id, f"✅ Removed {user.mention} from sudo user list"
            )
            return os.execvp("python3", ["python3", "-m", "Yukki"])
        await app.send_message(chat_id, f"Something wrong happened, check logs.")
        return
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    if user_id not in await get_sudoers():
        return await app.send_message(
            chat_id, f"❌ User is not a part of **group music**"
        )
    removed = await remove_sudo(user_id)
    if removed:
        await app.send_message(chat_id, f"✅ Removed {mention} from sudo user list")
        return os.execvp("python3", ["python3", "-m", "Yukki"])
    await app.send_message(chat_id, f"Something wrong happened, check logs.")


@app.on_message(filters.command("sudolist"))
async def sudoers_list(_, message: Message):
    chat_id = message.chat.id
    sudoers = await get_sudoers()
    text = "🧙🏻‍♂️ **List of sudo users:**\n\n"
    for user_id in enumerate(sudoers, 1):
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
        except Exception:
            continue
        text += f"➤ {user}\n"
    if not text:
        await app.send_message(chat_id, "❌ No sudo users found")
    else:
        await app.send_message(chat_id, text)
