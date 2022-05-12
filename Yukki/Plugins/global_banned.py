import asyncio

from Yukki import app, BOT_ID, OWNER
from Yukki.YukkiUtilities.database.gbanned import (
    is_gbanned_user,
    add_gban_user,
    add_gban_user,
    remove_gban_user,
)
from Yukki.YukkiUtilities.database.sudo import get_sudoers
from Yukki.YukkiUtilities.database.chats import get_served_chats
from pyrogram import filters
from pyrogram.errors import FloodWait


@app.on_message(filters.command("bl") & filters.user(OWNER))
async def ban_globally(_, message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        if len(message.command) < 2:
            await app.send_message(chat_id, "**Usage:**\n\n/bl [username/user_id]")
            return
        user = message.text.split(None, 2)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        sudoers = await get_sudoers()
        if user.id == from_user.id:
            return await app.send_message(chat_id, "You can't block yourself !")
        elif user.id == BOT_ID:
            await app.send_message(chat_id, "I can't block myself !")
        elif user.id in sudoers:
            await app.send_message(chat_id, "You can't block a sudo user !")
        else:
            await add_gban_user(user.id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await app.send_message(
                chat_id,
                f"🚷 **Globally banning {user.mention}**\n⏱ Expected time: `{len(served_chats)}`",
            )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user.id)
                    number_of_chats += 1
                    await asyncio.sleep(2)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
🚷 **New Global Ban On Group Music Bot**

**Origin:** {message.chat.title} [`{message.chat.id}`]
**Sudo User:** {from_user.mention}
**Banned User:** {user.mention}
**Banned User ID:** `{user.id}`
**Chats:** {number_of_chats}"""
            try:
                await m.delete()
            except Exception:
                pass
            await app.send_message(
                chat_id,
                f"{ban_text}",
                disable_web_page_preview=True,
            )
        return
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await app.send_message(chat_id, "You can't block yourself !")
    elif user_id == BOT_ID:
        await app.send_message(chat_id, "I can't block myself !")
    elif user_id in sudoers:
        await app.send_message(chat_id, "You can't block a sudo user !")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await app.send_message(chat_id, "✅ **User already gbanned.**")
        else:
            await add_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await app.send_message(
                chat_id,
                f"🚷 **Globally banning {mention}**\n⏱ Expected time: `{len(served_chats)}`",
            )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
🚷 **New Global Ban On Group Music Bot**

**Origin:** {message.chat.title} [`{message.chat.id}`]
**Sudo User:** {from_user_mention}
**Banned User:** {mention}
**Banned User ID:** `{user_id}`
**Chats:** {number_of_chats}"""
            try:
                await m.delete()
            except Exception:
                pass
            await app.send_message(
                chat_id,
                f"{ban_text}",
                disable_web_page_preview=True,
            )
            return


@app.on_message(filters.command("ungban") & filters.user(OWNER))
async def unban_globally(_, message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        if len(message.command) != 2:
            await app.send_message(
                chat_id, "**Usage:**\n\n/ungban [username / user_id]"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        sudoers = await get_sudoers()
        if user.id == from_user.id:
            await app.send_message(chat_id, "You can't unblock yourself !")
        elif user.id == BOT_ID:
            await app.send_message(chat_id, "I can't unblock myself !")
        elif user.id in sudoers:
            await app.send_message(chat_id, "Sudo users can't be blocked/unblocked.")
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await app.send_message(chat_id, "✅ User already ungbanned !")
            else:
                await remove_gban_user(user.id)
                await app.send_message(chat_id, f"✅ User ungbanned !")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await app.send_message(chat_id, "You can't unblock yourself !")
    elif user_id == BOT_ID:
        await app.send_message(chat_id, "I can't unblock myself, i'm not blocked !")
    elif user_id in sudoers:
        await app.send_message(chat_id, "Sudo users can't be blocked/unblocked.")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await app.send_message(chat_id, "✅ User already ungbanned !")
        else:
            await remove_gban_user(user_id)
            await app.send_message(chat_id, f"✅ User ungbanned !")


chat_watcher_group = 5


@app.on_message(group=chat_watcher_group)
async def chat_watcher_func(_, message):
    chat_id = message.chat.id
    try:
        userid = message.from_user.id
    except Exception:
        return
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_gbanned_user(userid):
        try:
            await message.chat.ban_member(userid)
        except Exception:
            return
        await app.send_message(
            chat_id,
            f"{checking} is globally banned by group msuic bot and has been kicked out from chat.\n\n🚫 **Reason:** potential spammer and abuser.",
        )
