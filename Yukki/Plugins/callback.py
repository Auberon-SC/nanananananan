import os
import re
import yt_dlp
import asyncio

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pytgcalls import StreamType
from youtubesearchpython import VideosSearch
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from Yukki import app, SUDOERS, aiohttpsession as session
from Yukki.config import LOG_GROUP_ID_2
from Yukki.YukkiUtilities.tgcallsrun import (
    yukki,
    convert,
    download,
    put,
    ASS_ACC,
)
from Yukki.YukkiUtilities.helpers.paste import paste
from Yukki.YukkiUtilities.database.queue import (
    is_active_chat,
    add_active_chat,
    music_on,
)
from Yukki.YukkiUtilities.database.playlist import (
    get_note_names,
    get_playlist,
    save_playlist,
    delete_playlist,
)
from Yukki.YukkiUtilities.helpers.inline import play_markup
from Yukki.YukkiUtilities.database.queue import (
    is_active_chat,
    add_active_chat,
    music_on,
)
from Yukki.YukkiUtilities.helpers.thumbnails import gen_thumb
from Yukki.YukkiUtilities.helpers.chattitle import CHAT_TITLE
from Yukki.YukkiUtilities.helpers.ytdl import ytdl_opts

pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")

flex = {}


async def isPreviewUp(preview: str) -> bool:
    for _ in range(7):
        try:
            async with session.head(preview, timeout=2) as resp:
                status = resp.status
                size = resp.content_length
        except asyncio.exceptions.TimeoutError:
            return False
        if status == 404 or (status == 200 and size == 0):
            await asyncio.sleep(0.4)
        else:
            return True if status == 200 else False
    return False


@Client.on_callback_query(filters.regex(pattern=r"ppcl"))
async def closesmex(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    try:
        user_id = callback_request.split("|")[1]
    except Exception as e:
        await CallbackQuery.message.edit(f"❌ An error occured\n\n**Reason:** `{e}`")
        return
    if CallbackQuery.from_user.id != int(user_id):
        await CallbackQuery.answer("💡 Sorry this is not your request", show_alert=True)
        return
    await CallbackQuery.message.delete()
    await CallbackQuery.answer()


@Client.on_callback_query(filters.regex("play_playlist"))
async def play_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    try:
        user_id, smex = callback_request.split("|")
    except Exception as e:
        await CallbackQuery.answer()
        return await CallbackQuery.message.edit(f"An error occured\n**Reason**: `{e}`")
    Name = CallbackQuery.from_user.first_name
    chat_title = CallbackQuery.message.chat.title
    if str(smex) == "personal":
        if CallbackQuery.from_user.id != int(user_id):
            return await CallbackQuery.answer(
                "💡 This is not your playlist", show_alert=True
            )
        _playlist = await get_note_names(CallbackQuery.from_user.id)
        if not _playlist:
            return await CallbackQuery.answer(
                f"❌ You not have playlist on database", show_alert=True
            )
        else:
            await CallbackQuery.message.delete()
            logger_text = f"""💡 Starting playlist

Group : {chat_title}
Request By : {Name}

▶ Personal playlist playing."""
            await ASS_ACC.send_message(
                LOG_GROUP_ID_2, f"{logger_text}", disable_web_page_preview=True
            )
            mystic = await CallbackQuery.message.reply_text(
                f"💡 Starting {Name}'s personal playlist.\n\n🎧 Request by: {CallbackQuery.from_user.first_name}"
            )
            checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
            msg = f"Queued Playlist:\n\n"
            j = 0
            for note in _playlist:
                _note = await get_playlist(CallbackQuery.from_user.id, note)
                title = _note["title"]
                videoid = _note["videoid"]
                url = f"https://www.youtube.com/watch?v={videoid}"
                duration = _note["duration"]
                if await is_active_chat(chat_id):
                    position = await put(chat_id, file=videoid)
                    j += 1
                    msg += f"{j}- {title[:50]}\n"
                    msg += f"Queued Position: {position}\n\n"
                    f20 = open(f"search/{videoid}id.txt", "w")
                    f20.write(f"{user_id}")
                    f20.close()
                else:
                    try:
                        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                            x = ytdl.extract_info(url, download=False)
                    except Exception as e:
                        return await mystic.edit(
                            f"Failed to download this track.\n\n**Reason:** {e}"
                        )
                    title = x["title"]

                    def my_hook(d):
                        if d["status"] == "downloading":
                            percentage = d["_percent_str"]
                            per = (
                                (str(percentage))
                                .replace(".", "", 1)
                                .replace("%", "", 1)
                            )
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
                                try:
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                except Exception as e:
                                    pass
                            if per > 250:
                                if flex[str(bytesx)] == 2:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}..\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                    print(
                                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                                    )
                            if per > 500:
                                if flex[str(bytesx)] == 3:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}...\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                    print(
                                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                                    )
                            if per > 800:
                                if flex[str(bytesx)] == 4:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}....\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                    print(
                                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                                    )
                        if d["status"] == "finished":
                            try:
                                taken = d["_elapsed_str"]
                            except Exception as e:
                                taken = "00:00"
                            size = d["_total_bytes_str"]
                            mystic.edit(
                                f"**Downloaded {title[:50]}.....**\n\n**Size:** `{size}` | **Time:** `{taken}` sec\n\n**Converting File** [__FFmpeg Processing__]"
                            )
                            print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")

                    loop = asyncio.get_event_loop()
                    xx = await loop.run_in_executor(None, download, url, my_hook)
                    file = await convert(xx)
                    await music_on(chat_id)
                    await add_active_chat(chat_id)
                    await yukki.pytgcalls.join_group_call(
                        chat_id,
                        InputStream(
                            InputAudioStream(
                                file,
                            ),
                        ),
                        stream_type=StreamType().pulse_stream,
                    )
                    ctitle = CallbackQuery.message.chat.title
                    ctitle = await CHAT_TITLE(ctitle)
                    thumb = await gen_thumb(videoid)
                    buttons = play_markup(videoid, user_id)
                    m = await CallbackQuery.message.reply_photo(
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(
                            f"🏷️ **Name:** [{title[:80]}]({url})\n⏱ **Duration:** `{duration}`\n💡 **Status:** `Playing`\n🎧 **Request by:** {checking}"
                        ),
                    )
                    os.remove(thumb)
                    await CallbackQuery.message.delete()
        await mystic.delete()
        m = await CallbackQuery.message.reply_text(
            "🔄 Pasting queued playlist to bin..."
        )
        link = await paste(msg)
        preview = link + "/preview.png"
        urlxp = link + "/index.txt"
        a1 = InlineKeyboardButton(text=f"Checkout Queued Playlist", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                ],
                [InlineKeyboardButton(text="🗑 Close", callback_data=f"close2")],
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview,
                    caption=f"This is queued personal playlist of {Name}.\n\nIf you want to delete any music from playlist use: /delmyplaylist",
                    quote=False,
                    reply_markup=key,
                )
                await m.delete()
            except Exception:
                pass
        else:
            await CallbackQuery.message.reply_text(text=msg, reply_markup=key)
            await m.delete()
    if str(smex) == "group":
        _playlist = await get_note_names(CallbackQuery.message.chat.id)
        if not _playlist:
            return await CallbackQuery.answer(
                f"This Group not have a playlist on database, try to adding music into playlist.",
                show_alert=True,
            )
        else:
            await CallbackQuery.message.delete()
            logger_text = f"""💡 Starting playlist

Group : `{chat_title}`
Request By : {Name}

▶ Group's playlist playing."""
            await ASS_ACC.send_message(
                LOG_GROUP_ID_2, f"{logger_text}", disable_web_page_preview=True
            )
            mystic = await CallbackQuery.message.reply_text(
                f"💡 Starting Groups's playlist.\n\n🎧 Request By: {CallbackQuery.from_user.first_name}"
            )
            checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
            msg = f"Queued Playlist:\n\n"
            j = 0
            for note in _playlist:
                _note = await get_playlist(CallbackQuery.message.chat.id, note)
                title = _note["title"]
                videoid = _note["videoid"]
                url = f"https://www.youtube.com/watch?v={videoid}"
                duration = _note["duration"]
                if await is_active_chat(chat_id):
                    position = await put(chat_id, file=videoid)
                    j += 1
                    msg += f"{j}- {title[:50]}\n"
                    msg += f"Queued Position: {position}\n\n"
                    f20 = open(f"search/{videoid}id.txt", "w")
                    f20.write(f"{user_id}")
                    f20.close()
                else:
                    try:
                        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                            x = ytdl.extract_info(url, download=False)
                    except Exception as e:
                        return await mystic.edit(
                            f"Failed to download this video.\n\n**Reason:** {e}"
                        )
                    title = x["title"]

                    def my_hook(d):
                        if d["status"] == "downloading":
                            percentage = d["_percent_str"]
                            per = (
                                (str(percentage))
                                .replace(".", "", 1)
                                .replace("%", "", 1)
                            )
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
                                try:
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                except Exception:
                                    pass
                            if per > 250:
                                if flex[str(bytesx)] == 2:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}..\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                    print(
                                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                                    )
                            if per > 500:
                                if flex[str(bytesx)] == 3:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}...\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                    print(
                                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                                    )
                            if per > 800:
                                if flex[str(bytesx)] == 4:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:
                                        mystic.edit(
                                            f"Downloading {title[:50]}....\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                        )
                                    print(
                                        f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds"
                                    )
                        if d["status"] == "finished":
                            try:
                                taken = d["_elapsed_str"]
                            except Exception as e:
                                taken = "00:00"
                            size = d["_total_bytes_str"]
                            mystic.edit(
                                f"**Downloaded: {title[:50]}...**\n\n**Size:** `{size}`\n**Time:** `{taken}` sec\n\n**Converting File** [__FFmpeg Processing__]"
                            )
                            print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")

                    loop = asyncio.get_event_loop()
                    xx = await loop.run_in_executor(None, download, url, my_hook)
                    file = await convert(xx)
                    await music_on(chat_id)
                    await add_active_chat(chat_id)
                    await yukki.pytgcalls.join_group_call(
                        chat_id,
                        InputStream(
                            InputAudioStream(
                                file,
                            ),
                        ),
                        stream_type=StreamType().pulse_stream,
                    )
                    ctitle = CallbackQuery.message.chat.title
                    ctitle = await CHAT_TITLE(ctitle)
                    thumb = await gen_thumb(videoid)
                    buttons = play_markup(videoid, user_id)
                    m = await CallbackQuery.message.reply_photo(
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(
                            f"🏷️ **Name:** [{title[:80]}]({url})\n⏱ **Duration:** `{duration}`\n💡 **Status:** `Playing`\n🎧 **Request by:** {checking}"
                        ),
                    )
                    os.remove(thumb)
                    await CallbackQuery.message.delete()
        await asyncio.sleep(1)
        await mystic.delete()
        m = await CallbackQuery.message.reply_text(
            "🔄 Pasting queued playlist to bin..."
        )
        link = await paste(msg)
        preview = link + "/preview.png"
        urlxp = link + "/index.txt"
        a1 = InlineKeyboardButton(text=f"Checkout Queued Playlist", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                ],
                [InlineKeyboardButton(text="🗑 Close", callback_data=f"close2")],
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview,
                    caption=f"This is queued playlist of this Group.\n\nIf you want to delete any music from playlist use: /delchatplaylist",
                    quote=False,
                    reply_markup=key,
                )
                await m.delete()
            except Exception:
                pass
        else:
            await CallbackQuery.message.reply_text(text=msg, reply_markup=key)
            await m.delete()


@Client.on_callback_query(filters.regex("group_playlist"))
async def group_playlist(_, CallbackQuery):
    await CallbackQuery.answer()
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "You must be admin with permissions:\n\n❌ » Manage video chat",
            show_alert=True,
        )
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    try:
        url = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(
            f"❌ An error occured\n\n**Reason:** `{e}`"
        )
    Name = CallbackQuery.from_user.mention
    _count = await get_note_names(chat_id)
    count = 0
    if not _count:
        sex = await CallbackQuery.message.reply_text(
            "💡 Generating Group's playlist in database..."
        )
        await asyncio.sleep(2)
        await sex.delete()
    else:
        for smex in _count:
            count += 1
    count = int(count)
    if count == 30:
        return await CallbackQuery.message.reply_text(
            "💡 Sorry you can only have 30 music in Group's playlist."
        )
    try:
        url = f"https://www.youtube.com/watch?v={url}"
        results = VideosSearch(url, limit=1)
        for result in results.result()["result"]:
            title = result["title"]
            duration = result["duration"]
            videoid = result["id"]
    except Exception as e:
        return await CallbackQuery.message.reply_text(
            f"❌ An error occured.\n\nPlease forward to @FumikaSupportGroup\n\n**Reason:** `{e}`"
        )
    _check = await get_playlist(chat_id, videoid)
    title = title[:50]
    if _check:
        return await CallbackQuery.message.reply_text(
            f"{Name}, your request is already **added** to the **playlist !**"
        )
    assis = {
        "videoid": videoid,
        "title": title,
        "duration": duration,
    }
    await save_playlist(chat_id, videoid, assis)
    Name = CallbackQuery.from_user.mention
    return await CallbackQuery.message.reply_text(
        f"✅ Added to **Group's playlist**\n │\n └ **Request by:** {Name}"
    )


@Client.on_callback_query(filters.regex("playlist"))
async def pla_playylistt(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    try:
        url = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(
            f"❌ An error occured\n\n**Reason:** `{e}`"
        )
    Name = CallbackQuery.from_user.mention
    _count = await get_note_names(userid)
    count = 0
    if not _count:
        sex = await CallbackQuery.message.reply_text(
            "💡 Generating your personal playlist in database..."
        )
        await asyncio.sleep(2)
        await sex.delete()
    else:
        for smex in _count:
            count += 1
    count = int(count)
    if count == 30:
        if userid in SUDOERS:
            pass
        else:
            return await CallbackQuery.message.reply_text(
                "💡 Sorry you can only have 30 music in your playlist."
            )
    try:
        url = f"https://www.youtube.com/watch?v={url}"
        results = VideosSearch(url, limit=1)
        for result in results.result()["result"]:
            title = result["title"]
            duration = result["duration"]
            videoid = result["id"]
    except Exception as e:
        return await CallbackQuery.message.reply_text(
            f"An error occured.\n\nPlease forward to @punyazein\n**Possible Reason:**{e}"
        )
    _check = await get_playlist(userid, videoid)
    if _check:
        return await CallbackQuery.message.reply_text(
            f"{Name}, your request is **already added** to the **playlist !**"
        )
    title = title[:50]
    assis = {
        "videoid": videoid,
        "title": title,
        "duration": duration,
    }
    await save_playlist(userid, videoid, assis)
    return await CallbackQuery.message.reply_text(
        f"✅ Added to **personal playlist**\n │\n └ **Request by:** {Name}"
    )


@Client.on_callback_query(filters.regex("P_list"))
async def P_list(_, CallbackQuery):
    _playlist = await get_note_names(CallbackQuery.from_user.id)
    if not _playlist:
        return await CallbackQuery.answer(
            f"❌ You not have personal playlist on database, try to adding music in playlist.",
            show_alert=True,
        )
    else:
        j = 0
        await CallbackQuery.answer()
        msg = f"Personal Playlist:\n\n"
        for note in _playlist:
            j += 1
            _note = await get_playlist(CallbackQuery.from_user.id, note)
            title = _note["title"]
            duration = _note["duration"]
            msg += f"{j}- {title[:60]}\n"
            msg += f"Duration: {duration} min(s)\n\n"
        await CallbackQuery.answer()
        await CallbackQuery.message.delete()
        m = await CallbackQuery.message.reply_text("🔄 Pasting playlist to bin...")
        link = await paste(msg)
        preview = link + "/preview.png"
        print(link)
        urlxp = link + "/index.txt"
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
        a2 = InlineKeyboardButton(
            text=f"💡 Play {user_name[:17]}'s playlist",
            callback_data=f"play_playlist {user_id}|personal",
        )
        a3 = InlineKeyboardButton(text=f"🔗 Check Playlist", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a2,
                ],
                [a3, InlineKeyboardButton(text="🗑 Close", callback_data=f"close2")],
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview, quote=False, reply_markup=key
                )
                await m.delete()
            except Exception as e:
                print(e)
                pass
        else:
            print("5")
            await CallbackQuery.message.reply_photo(
                photo=link, quote=False, reply_markup=key
            )
            await m.delete()


@Client.on_callback_query(filters.regex("G_list"))
async def G_list(_, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    _playlist = await get_note_names(CallbackQuery.message.chat.id)
    if not _playlist:
        return await CallbackQuery.answer(
            f"❌ You not have Group playlist on database, try to adding music into playlist.",
            show_alert=True,
        )
    else:
        await CallbackQuery.answer()
        j = 0
        msg = f"Group Playlist:\n\n"
        for note in _playlist:
            j += 1
            _note = await get_playlist(CallbackQuery.message.chat.id, note)
            title = _note["title"]
            duration = _note["duration"]
            msg += f"{j}- {title[:60]}\n"
            msg += f"    Duration: {duration} Min(s)\n\n"
        await CallbackQuery.answer()
        await CallbackQuery.message.delete()
        m = await CallbackQuery.message.reply_text("🔄 Pasting playlist to bin...")
        link = await paste(msg)
        preview = link + "/preview.png"
        urlxp = link + "/index.txt"
        user_id = CallbackQuery.from_user.id
        a1 = InlineKeyboardButton(
            text=f"💡 Play Group's playlist",
            callback_data=f"play_playlist {user_id}|group",
        )
        a3 = InlineKeyboardButton(text=f"🔗 Check Playlist", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                ],
                [a3, InlineKeyboardButton(text="🗑 Close", callback_data=f"close2")],
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview, quote=False, reply_markup=key
                )
                await m.delete()
            except Exception:
                pass
        else:
            await CallbackQuery.message.reply_photo(
                photo=link, quote=False, reply_markup=key
            )
            await m.delete()


@Client.on_callback_query(filters.regex("cbgroupdel"))
async def cbgroupdel(_, CallbackQuery):
    a = await app.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer(
            "You must be admin with permissions:\n\n❌ » manage_video_chats",
            show_alert=True,
        )
    _playlist = await get_note_names(CallbackQuery.message.chat.id)
    if not _playlist:
        return await CallbackQuery.answer(
            "❌ This Group has no playlist in database.", show_alert=True
        )
    else:
        for note in _playlist:
            await delete_playlist(CallbackQuery.message.chat.id, note)
    await CallbackQuery.answer(
        "✅ The whole Group's playlist has been deleted", show_alert=True
    )
    if CallbackQuery.message.reply_to_message:
        await CallbackQuery.message.reply_to_message.delete()
        return await CallbackQuery.message.delete()
    else:
        return await CallbackQuery.message.delete()


@Client.on_callback_query(filters.regex("cbdel"))
async def delplcb(_, CallbackQuery):
    _playlist = await get_note_names(CallbackQuery.from_user.id)
    if not _playlist:
        return await CallbackQuery.answer(
            "❌ You not have a personal playlist in database.", show_alert=True
        )
    else:
        for note in _playlist:
            await delete_playlist(CallbackQuery.from_user.id, note)
    await CallbackQuery.answer(
        "✅ The whole of your personal playlist has been deleted", show_alert=True
    )
    if CallbackQuery.message.reply_to_message:
        await CallbackQuery.message.reply_to_message.delete()
        return await CallbackQuery.message.delete()
    else:
        return await CallbackQuery.message.delete()
