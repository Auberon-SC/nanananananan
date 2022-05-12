from pyrogram import filters, Client
from Yukki import SUDOERS, app
from Yukki.YukkiUtilities.database.onoff import add_on, add_off
from Yukki.YukkiUtilities.helpers.filters import command


@Client.on_message(command("musicp") & filters.user(SUDOERS))
async def smex(_, message):
    chat_id = message.chat.id
    usage = "**Usage:**\n/maintenance [enable|disable]"
    if len(message.command) != 2:
        return await app.send_message(chat_id, usage)
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        user_id = 1
        await add_on(user_id)
        await app.send_message(
            chat_id,
            "✅ Maintenance mode enabled\n\n• From now on, user can't play music after the maintenance mode is disabled.",
        )
    elif state == "disable":
        user_id = 1
        await add_off(user_id)
        await app.send_message(
            chat_id,
            "❌ Maintenance mode disabled\n\n• From now on, user can play music again.",
        )
    else:
        await app.send_message(chat_id, usage)


@Client.on_message(command("sptest") & filters.user(SUDOERS))
async def sls_skfs(_, message):
    chat_id = message.chat.id
    usage = "**Usage:**\n/speedtest [enable|disable]"
    if len(message.command) != 2:
        return await app.send_message(chat_id, usage)
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        user_id = 2
        await add_on(user_id)
        await app.send_message(chat_id, "✅ **Speedtest enabled**")
    elif state == "disable":
        user_id = 2
        await add_off(user_id)
        await app.send_message(chat_id, "❌ **Speedtest disabled**")
    else:
        await app.send_message(chat_id, usage)
