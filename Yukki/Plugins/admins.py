import yt_dlp
import asyncio
import time as sedtime

from asyncio import QueueEmpty
from pyrogram import filters, Client
from pyrogram.types import (
    InlineKeyboardMarkup,
    Message,
    InlineKeyboardButton,
    CallbackQuery,
)
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from Yukki.config import admins
from Yukki import app, BOT_USERNAME
from Yukki.YukkiUtilities.tgcallsrun import (
    yukki,
    convert,
    download,
    clear,
    get,
    is_empty,
    task_done,
)
from Yukki.YukkiUtilities.tgcallsrun.yukki import pytgcalls as call_py
from Yukki.YukkiUtilities.tgcallsrun.queues import QUEUE, clear_queue
from Yukki.YukkiUtilities.tgcallsrun.video import skip_current_song, skip_item
from Yukki.YukkiUtilities.helpers.decorators import authorized_users_only
from Yukki.YukkiUtilities.helpers.filters import command
from Yukki.YukkiUtilities.helpers.chattitle import CHAT_TITLE
from Yukki.YukkiUtilities.helpers.ytdl import ytdl_opts
from Yukki.YukkiUtilities.helpers.inline import close_keyboard
from Yukki.YukkiUtilities.database.queue import (
    is_active_chat,
    remove_active_chat,
    music_on,
    is_music_playing,
    music_off,
)


flex = {}


bttn = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="cbmenu")]])


bcl = InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="cls")]])


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = await app.get_chat_member(chat_id, user_id)
    if member.can_manage_voice_chats:
        perms.append("can_manage_voice_chats")
    return perms


from Yukki.YukkiUtilities.helpers.administrator import adminsOnly


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


@app.on_message(filters.command("cleandb"))
async def stop_cmd(
    _, message
):  # clean database of current chat (used by admin group only)
    chat_id = message.chat.id
    try:
        clear(message.chat.id)
    except QueueEmpty:
        pass
    await remove_active_chat(chat_id)
    try:
        await yukki.pytgcalls.leave_group_call(message.chat.id)
    except:
        pass
    await app.send_message(
        message.chat.id,
        f"✅ __Erased queues, logs, raw_files, downloads and databases in **{message.chat.title}**__\n│\n╰ Database cleaned by {message.from_user.mention}.",
    )


@app.on_message(filters.command("pause"))
async def pause_cmd(_, message):
    if message.sender_chat:
        return await message.send_message(
            message.chat.id,
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account.",
        )
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    chat_id = message.chat.id
    if not await is_active_chat(chat_id):
        return await app.send_message(chat_id, "❌ **No music is currently playing**")
    elif not await is_music_playing(message.chat.id):
        return await app.send_message(chat_id, "❌ **No music is currently playing**")
    await music_off(chat_id)
    await yukki.pytgcalls.pause_stream(chat_id)
    await app.send_message(
        message.chat.id,
        "⏸ **Music playback paused**.\n\n• To resume streaming, can use » /resume commands.",
    )


@app.on_message(filters.command("resume"))
async def stop_cmd(_, message):
    if message.sender_chat:
        return await message.send_message(
            message.chat.id,
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account.",
        )
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    chat_id = message.chat.id
    if not await is_active_chat(chat_id):
        return await app.send_message(
            message.chat.id, "❌ **No music is currently playing**"
        )
    elif await is_music_playing(message.chat.id):
        return await app.send_message(
            message.chat.id, "❌ **No music is currently playing**"
        )
    else:
        await music_on(chat_id)
        await yukki.pytgcalls.resume_stream(message.chat.id)
        await app.send_message(
            message.chat.id,
            "▶️ Music playback resumed.\n\n• To pause streaming, can use » /pause commands.",
        )


@app.on_message(filters.command(["stop", "end"]))
async def stop_cmd(_, message):
    if message.sender_chat:
        return await message.send_message(
            message.chat.id,
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account.",
        )
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    chat_id = message.chat.id
    if await is_active_chat(chat_id):
        try:
            clear(message.chat.id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await yukki.pytgcalls.leave_group_call(message.chat.id)
        await app.send_message(
            message.chat.id, "✅ __Userbot has been disconnected from voice chat.__"
        )
    else:
        return await app.send_message(
            message.chat.id, "❌ **No music is currently playing**"
        )


@app.on_message(filters.command(["skip", "next"]))
async def stop_cmd(_, message):
    if message.sender_chat:
        return await app.send_message(
            message.chat.id,
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account.",
        )
    permission = "can_manage_voice_chats"
    m = await adminsOnly(permission, message)
    if m == 1:
        return
    chat_id = message.chat.id
    chat_title = message.chat.title
    if not await is_active_chat(chat_id):
        await app.send_message(message.chat.id, "❌ **No music is currently playing**")
    else:
        task_done(chat_id)
        if is_empty(chat_id):
            await remove_active_chat(chat_id)
            await app.send_message(
                message.chat.id,
                "❌ No more music in __Queues__ \n\n» Userbot leaving video chat",
            )
            await yukki.pytgcalls.leave_group_call(message.chat.id)
            return
        else:
            afk = get(chat_id)["file"]
            f1 = afk[0]
            f2 = afk[1]
            f3 = afk[2]
            finxx = f"{f1}{f2}{f3}"
            if str(finxx) != "raw":
                mystic = await app.send_message(
                    message.chat.id, "📥 Downloading next music from playlist..."
                )
                url = f"https://www.youtube.com/watch?v={afk}"
                try:
                    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                        x = ytdl.extract_info(url, download=False)
                except Exception as e:
                    return await mystic.edit_text(
                        f"Failed to download this track.\n\n**Reason**: `{e}`"
                    )
                title = x["title"]
                videoid = afk

                def my_hook(d):
                    if d["status"] == "downloading":
                        percentage = d["_percent_str"]
                        per = (str(percentage)).replace(".", "", 1).replace("%", "", 1)
                        per = int(per)
                        eta = d["eta"]
                        speed = d["_speed_str"]
                        size = d["_total_bytes_str"]
                        bytesx = d["total_bytes"]
                        if str(bytesx) in flex:
                            pass
                        else:
                            flex[str(bytesx)] = 1
                        if flex[str(bytesx)] == 1:
                            flex[str(bytesx)] += 1
                            sedtime.sleep(1)
                            mystic.edit(
                                f"Downloading {title[:50]}\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                            )
                        if per > 500:
                            if flex[str(bytesx)] == 2:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(
                                    f"Downloading {title[:50]}...\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                )
                                print(
                                    f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds"
                                )
                        if per > 800:
                            if flex[str(bytesx)] == 3:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(
                                    f"Downloading {title[:50]}....\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                )
                                print(
                                    f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds"
                                )
                        if per == 1000:
                            if flex[str(bytesx)] == 4:
                                flex[str(bytesx)] = 1
                                sedtime.sleep(0.5)
                                mystic.edit(
                                    f"Downloading {title[:50]}.....\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                )
                                print(
                                    f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds"
                                )

                loop = asyncio.get_event_loop()
                xxx = await loop.run_in_executor(None, download, url, my_hook)
                file = await convert(xxx)
                await yukki.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            file,
                        ),
                    ),
                )
                ctitle = (await app.get_chat(chat_id)).title
                ctitle = await CHAT_TITLE(ctitle)
                f2 = open(f"search/{afk}id.txt", "r")
                await app.send_message(
                    message.chat.id, "⏭ **Skipped to the next track**"
                )
            else:
                await yukki.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            afk,
                        ),
                    ),
                )
                _chat_ = (
                    (str(afk))
                    .replace("_", "", 1)
                    .replace("/", "", 1)
                    .replace(".", "", 1)
                )
                f2 = open(f"search/{_chat_}title.txt", "r")
                title = f2.read()
                f3 = open(f"search/{_chat_}duration.txt", "r")
                f4 = open(f"search/{_chat_}username.txt", "r")
                f4 = open(f"search/{_chat_}videoid.txt", "r")
                videoid = f4.read()
                videoid = str(videoid)
                await app.send_message(
                    message.chat.id, "⏭ **Skipped to the next track**"
                )
                return


@app.on_message(filters.command(["reload", f"reload@{BOT_USERNAME}"]))
async def update_admins(_, message):
    chat_id = message.chat.id
    global admins
    new_admins = []
    new_ads = await app.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    msg = await app.send_message(
        chat_id, "✅ Bot reloaded correctly!\n\n• The admin list has been updated."
    )
    await asyncio.sleep(10)
    await msg.delete()


@Client.on_callback_query(filters.regex("cbmenu"))
async def cbmenu(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Only admins with voice chat manage permission can tap this button!",
            show_alert=True,
        )
    await query.edit_message_text(
        f"⚙️ **Settings of** {query.message.chat.title}\n\nII : Pause Streaming\n▷ : Resume Streaming\n🔇 : Mute Assistant\n🔊 : Unmute Assistant\n▢ : Stop Streaming",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("▢", callback_data="cbstop"),
                    InlineKeyboardButton("II", callback_data="cbpause"),
                    InlineKeyboardButton("▷", callback_data="cbresume"),
                ],
                [
                    InlineKeyboardButton("🔇", callback_data="cbmute"),
                    InlineKeyboardButton("🔊", callback_data="cbunmute"),
                ],
                [InlineKeyboardButton("Close", callback_data="cls")],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("cls"))
async def close(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Only admins with voice chat manage permission can tap this button!",
            show_alert=True,
        )
    await query.message.delete()


@app.on_message(command(["vskip"]) & filters.group)
@authorized_users_only
async def skip(client, m: Message):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="• Mᴇɴᴜ​ •", callback_data="cbmenu"),
            ]
        ]
    )

    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await app.send_message(chat_id, "❌ No video is currently streaming")
        elif op == 1:
            await app.send_message(
                chat_id, "__Queue__ **empty.**\n\n**• Assistant leaves voice chat**"
            )
        elif op == 2:
            await app.send_message(
                chat_id,
                "🗑️ **Clearing the Queue**\n\n**• Assistant leaves voice chat**",
            )
        else:
            await app.send_message(
                chat_id,
                f"""
⏭️ **Playing {op[2]} next**
🏷 **Name:** [{op[0]}]({op[1]})
🎧 **Request by:** {m.from_user.mention()}
""",
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "🗑 **Song removed from queue:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#{x}** - {hm}"
            await m.reply(OP)


@app.on_message(command(["vstop"]) & filters.group)
@authorized_users_only
async def stop(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await app.send_message(
                m.chat.id, "✅ __The Userbot has disconnected from the video chats.__"
            )
        except Exception as e:
            await app.send_message(m.chat.id, f"**Error:**\n\n`{e}`")
    else:
        await app.send_message(m.chat.id, "❌ **No video is currently streaming**")


@app.on_message(command(["vpause"]) & filters.group)
@authorized_users_only
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await app.send_message(
                m.chat.id,
                "II **Video playback paused.**\n\n• To resume video streaming, can use » /vresume commands",
                reply_markup=close_keyboard,
            )
        except Exception as e:
            await app.send_message(m.chat.id, f"**Error:**\n\n`{e}`")
    else:
        await app.send_message(m.chat.id, "❌ **No video is currently streaming**")


@app.on_message(command(["vresume"]) & filters.group)
@authorized_users_only
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await app.send_message(
                m.chat.id,
                "▷ **Video playback resumed.**\n\n• To pause video streaming, can use » /vpause commands",
                reply_markup=close_keyboard,
            )
        except Exception as e:
            await app.send_message(m.chat.id, f"**Error:**\n\n`{e}`")
    else:
        await app.send_message(m.chat.id, "❌ **No video is currently streaming**")


@app.on_message(command(["vmute"]) & filters.group)
@authorized_users_only
async def mute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await app.send_message(
                m.chat.id,
                "🔇 **Assistant muted.**\n\n• To activate the Assistant voice, can use » /vunmute commands",
                reply_markup=close_keyboard,
            )
        except Exception as e:
            await app.send_message(m.chat.id, f"**Error:**\n\n`{e}`")
    else:
        await app.send_message(m.chat.id, "❌ **No video is currently streaming**")


@app.on_message(command(["vunmute"]) & filters.group)
@authorized_users_only
async def unmute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await app.send_message(
                m.chat.id,
                "🔊 **Assistant activated.**\n\n• To muted the Assistant voice, can use » /vmute commands",
                reply_markup=close_keyboard,
            )
        except Exception as e:
            await app.send_message(m.chat.id, f"**Error:**\n\n`{e}`")
    else:
        await app.send_message(m.chat.id, "❌ **No video is currently streaming**")


@Client.on_callback_query(filters.regex("cbpause"))
async def cbpause(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Only admins with voice chat manage permission can tap this button!",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await query.edit_message_text(
                "II Streaming has been paused", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ No video is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbresume"))
async def cbresume(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Only admins with voice chat manage permission can tap this button!",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await query.edit_message_text("▷ Streaming has resumed", reply_markup=bttn)
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ No video is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbstop"))
async def cbstop(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Only admins with voice chat manage permission can tap this button!",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await query.edit_message_text("✅ **Streaming has ended**", reply_markup=bcl)
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ No video is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbmute"))
async def cbmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Only admins with voice chat manage permission can tap this button!",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await query.edit_message_text(
                "🔇 Assistant successfully muted", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"***Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ No video is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbunmute"))
async def cbunmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer(
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account."
        )
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer(
            "💡 Only admins with voice chat manage permission can tap this button!",
            show_alert=True,
        )
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await query.edit_message_text(
                "🔊 Assistant successfully unmuted", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"**Error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("❌ No video is currently streaming", show_alert=True)


@app.on_message(command(["volume", "vol"]))
@authorized_users_only
async def change_volume(client, m: Message):
    chat_id = m.chat.id
    if len(m.command) < 2:
        await app.send_message(
            chat_id,
            "Please provide a number from 0-200 to set the volume in video chat",
            reply_markup=close_keyboard,
        )
        return
    if chat_id in QUEUE:
        try:
            await call_py.change_volume_call(chat_id, volume=int(range))
            await app.send_message(
                m.chat.id,
                f"✅ Volume has been successfully set to `{range}`%",
                reply_markup=close_keyboard,
            )
        except Exception as e:
            await app.send_message(m.chat.id, f"**Error:**\n\n`{e}`")
    else:
        await app.send_message(m.chat.id, "❌ **No video is currently streaming**")
