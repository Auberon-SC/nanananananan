from pyrogram import Client
from Yukki import app
from Yukki.YukkiUtilities.database.playlist import (
    get_note_names,
    get_playlist,
    delete_playlist,
)
from Yukki.YukkiUtilities.helpers.inline import (
    confirm_keyboard,
    play_list_keyboard,
    confirm_group_keyboard,
)
from Yukki.YukkiUtilities.helpers.filters import command, other_filters


options = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "all",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
]


@Client.on_message(command(["playlist", "playlist@FumikaRobot"]) & other_filters)
async def start_playlist_cmd(_, message):
    chat_id = message.chat.id
    await app.send_message(
        chat_id,
        "❓ Which playlist do you want to play ?",
        reply_markup=play_list_keyboard,
    )
    return


@Client.on_message(
    command(["delmyplaylist", "delmyplaylist@RessoStreamBot"]) & other_filters
)
async def delmyplaylist(_, message):
    chat_id = message.chat.id
    usage = "Usage:\n\n/delmyplaylist [numbers between 1-30] (to delete a particular music in playlist)\n\n/delmyplaylist all (to delete whole playlist)"
    if len(message.command) < 2:
        return await app.send_message(chat_id, usage)
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await app.send_message(chat_id, usage)
    if name not in options:
        return await app.send_message(chat_id, usage)
    if len(message.text) == 18:
        return await app.send_message(
            chat_id,
            f"💡 **Confirmation** !\n\nThe playlist will be lost, are you sure want to delete your whole playlist ?",
            reply_markup=confirm_keyboard,
        )
    else:
        _playlist = await get_note_names(message.from_user.id)
    if not _playlist:
        await app.send_message(chat_id, "You not have playlist on database !")
    else:
        j = 0
        count = int(name)
        for note in _playlist:
            j += 1
            await get_playlist(message.from_user.id, note)
            if j == count:
                deleted = await delete_playlist(message.from_user.id, note)
                if deleted:
                    return await app.send_message(
                        chat_id, f"✅ Deleted the `{count}` music in personal playlist"
                    )
                else:
                    return await app.send_message(
                        chat_id, "No such saved music in playlist !"
                    )
        await message.reply_text("You not have such music in playlist !")


@Client.on_message(
    command(["delchatplaylist", "delchatplaylist@FumikaRobot"]) & other_filters
)
async def delchatplaylist(_, message):
    chat_id = message.chat.id
    a = await app.get_chat_member(message.chat.id, message.from_user.id)
    if not a.can_manage_voice_chats:
        return app.send_message(
            chat_id,
            "You're missing admin rights to use this command.\n\n» ❌ can_manage_voice_chats",
        )
    usage = "Usage:\n\n/delchatplaylist [numbers between 1-30] (to delete a particular music in playlist)\n\n/delchatplaylist all (to delete whole playlist)"
    if len(message.command) < 2:
        return await app.send_message(chat_id, usage)
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await app.send_message(chat_id, usage)
    if name not in options:
        return await app.send_message(chat_id, usage)
    if len(message.text) == 21:
        return await app.send_message(
            chat_id,
            f"💡 Confirmation !\n\nThe playlist will be lost, are you sure want to delete your whole Group playlist ?",
            reply_markup=confirm_group_keyboard,
        )
    else:
        _playlist = await get_note_names(message.chat.id)
    if not _playlist:
        await app.send_message(chat_id, "Group's has no playlist on database !")
    else:
        j = 0
        count = int(name)
        for note in _playlist:
            j += 1
            await get_playlist(message.chat.id, note)
            if j == count:
                deleted = await delete_playlist(message.chat.id, note)
                if deleted:
                    return await app.send_message(
                        chat_id,
                        f"**✅ Deleted the `{count}` music in group's playlist**",
                    )
                else:
                    return await app.send_message(
                        chat_id, f"**No such saved music in group playlist !**"
                    )
        await app.send_message(chat_id, "You not have such music in Group's playlist !")
