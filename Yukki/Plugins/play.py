import os
import shutil
import random
import asyncio
import yt_dlp
import shutil

from os import path
from asyncio import QueueEmpty
from datetime import datetime, timedelta
from youtubesearchpython import VideosSearch
from pytgcalls import StreamType
from pytgcalls.exceptions import NoActiveGroupCall, GroupCallNotFound
from pytgcalls.types.input_stream import InputAudioStream, InputStream, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)

from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
    Voice,
)
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant, ChatAdminRequired, ChannelPrivate, ChatForbidden, PeerIdInvalid
from Yukki import (
    app,
    BOT_USERNAME,
    BOT_ID,
    ASSID,
    BOT_NAME,
    db_mem,
    ASSNAME,
)
from Yukki.converter.cli import userbot
from Yukki.config import DURATION_LIMIT, GROUP, CHANNEL, LOG_GROUP_ID_2
from Yukki.YukkiUtilities.tgcallsrun import (
    yukki,
    convert,
    download,
    put,
    ASS_ACC,
)
from Yukki.YukkiUtilities.tgcallsrun.yukki import pytgcalls
from Yukki.YukkiUtilities.tgcallsrun.queues import (
    QUEUE,
    add_to_queue,
    clear,
    get_queue,
)
from Yukki.YukkiUtilities.database import is_autoend
from Yukki.YukkiUtilities.database.queue import (
    is_active_chat,
    add_active_chat,
    remove_active_chat,
    music_on,
)
from Yukki.YukkiUtilities.database.onoff import is_on_off
from Yukki.YukkiUtilities.helpers.inline import (
    search_markup,
    play_markup,
    playlist_markup,
    audio_markup,
    close_keyboard,
    search_markup2,
)
from Yukki.YukkiUtilities.helpers.filters import command, other_filters
from Yukki.YukkiUtilities.helpers.gets import get_url, themes
from Yukki.YukkiUtilities.helpers.logger import LOG_CHAT
from Yukki.YukkiUtilities.helpers.thumbnails import gen_thumb
from Yukki.YukkiUtilities.helpers.chattitle import CHAT_TITLE
from Yukki.YukkiUtilities.helpers.ytdl import ytdl_opts
from Yukki.YukkiUtilities.helpers.administrator import unauthorised
from Yukki.YukkiUtilities.helpers.decorators import authorized_users_only

flex = {}
chat_watcher_group = 3

DISABLED_GROUPS = []
useer = "NaN"
que = {}
chat_id = None

autoend = {}
counter = {}
AUTO_END_TIME = 3

MUST_JOIN = os.getenv("MUST_JOIN")


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@app.on_message(
    command(["musicplayer", f"musicplayer@{BOT_USERNAME}"])
    & ~filters.edited
    & ~filters.bot
    & ~filters.private
)
@authorized_users_only
async def music_onoff(_, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    global DISABLED_GROUPS
    try:
        user_id
    except:
        return
    if len(message.command) != 2:
        await app.send_message(
            chat_id,
            "😕 **Incorrect command syntax.**\n\n» Try `/musicplayer on` or `/musicplayer off`",
            reply_markup=close_keyboard,
        )
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status in ("ON", "on", "On"):
        lel = await app.send_message(chat_id, "`Processing...`")
        if not message.chat.id in DISABLED_GROUPS:
            await lel.edit("» **Music player already turned on.**")
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"✅ **Music player turned on.**\n\n• Now, users in {message.chat.title} can playing music."
        )

    elif status in ("OFF", "off", "Off"):
        lel = await app.send_message(chat_id, "`Processing...`")

        if message.chat.id in DISABLED_GROUPS:
            await lel.edit("» **Music player already turned off.**")
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"✅ **Music player turned off.**\n\n• Now, users in {message.chat.title} cannot playing music."
        )
    else:
        await app.send_message(
            chat_id,
            "😕 **Incorrect command syntax.**\n\n» Try `/musicplayer on` or `/musicplayer off`",
            reply_markup=close_keyboard,
        )


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
async def play(_, message: Message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    if not MUST_JOIN:  # Not compulsory
        return
    try:
        try:
            await app.get_chat_member(MUST_JOIN, message.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await app.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await message.reply(
                    f"**Halo {rpk} Untuk menghindari penggunaan yang berlebihan bot ini di khususkan untuk yang sudah join di channel kami!**",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("✨ Join Channel ✨", url=link)]]
                    ),
                )
                await message.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"Masukkan SI ANJING ke dalam @{MUST_JOIN} dan jadikan admin")
    if message.sender_chat:
        return await app.send_message(
            chat_id,
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account from admin rights.",
        )
    global useer
    if chat_id in DISABLED_GROUPS:
        return await app.send_message(
            chat_id,
            f"😕 **Sorry {message.from_user.mention}, Musicplayer has turned off by admin.**\n\n» Ask admin to type `/musicplayer on` in this group.",
            reply_markup=close_keyboard,
        )
    user_id = message.from_user.id
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_on_off(1):
        LOG_ID = "-1001306851903"
        if int(chat_id) != int(LOG_ID):
            return await app.send_message(
                chat_id, "» Bot is under maintenance, sorry for the inconvenience!"
            )
    a = await app.get_chat_member(message.chat.id, BOT_ID)
    if a.status != "administrator":
        await app.send_message(
            chat_id,
            f"💡 To use me, I need to be an Administrator with the following permissions:\n\n» ❌ __Delete messages__\n» ❌ __Add users__\n» ❌ __Manage video chat__\n\nData is **updated** automatically after you **promote me**",
        )
        return
    if not a.can_manage_voice_chats:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Manage Video Chats__\n\nOnce done, try again.",
        )
        return
    if not a.can_delete_messages:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Delete Messages__\n\nOnce done, try again.",
        )
        return
    if not a.can_invite_users:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Invite Users via Link__\n\nOnce done, try again.",
        )
        return
    if not a.can_restrict_members:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Ban Users__\n\nOnce done, try again.",
        )
        return
    if not a.can_promote_members:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Add New Admins__\n\nOnce done, try again.",
        )
        return
    if not a.can_pin_messages:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Pin Messages__\n\nOnce done, try again.",
        )
        return
    if not a.can_change_info:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Change Group Info__\n\nOnce done, try again.",
        )
        return
    try:
        b = await app.get_chat_member(message.chat.id, ASSID)
        if b.status == "banned" or b.status == "kicked":
            await app.unban_chat_member(message.chat.id, ASSID)
            invite_link = await app.export_chat_invite_link(message.chat.id)
            if "+" in invite_link:
                kontol = (invite_link.replace("+", "")).split("t.me/")[1]
                link_bokep = f"https://t.me/joinchat/{kontol}"
            await ASS_ACC.join_chat(link_bokep)
            await app.promote_chat_member(
                message.chat.id,
                ASSID,
                can_manage_voice_chats=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_pin_messages=True,
                can_change_info=True,
            )
    except UserNotParticipant:
        try:
            invite_link = await app.export_chat_invite_link(message.chat.id)
            if "+" in invite_link:
                kontol = (invite_link.replace("+", "")).split("t.me/")[1]
                link_bokep = f"https://t.me/joinchat/{kontol}"
            await ASS_ACC.join_chat(link_bokep)
            await app.promote_chat_member(
                message.chat.id,
                ASSID,
                can_manage_voice_chats=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_pin_messages=True,
                can_change_info=True,
            )
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            return await app.send_message(
                chat_id,
                f"❌ **An error when {ASSNAME} joining**\n\n**Reason**:`{e}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🗑️ Close", callback_data="close")]]
                ),
            )
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)
    fucksemx = 0
    if audio:
        fucksemx = 1
        mystic = await app.send_message(chat_id, "🔄 Converting audio...")
        if audio.file_size > 157286400:
            await mystic.edit_text("Audio file size must be less than `150` mb")
            return
        duration = round(audio.duration / 60)
        if duration > DURATION_LIMIT:
            return await mystic.edit_text(
                f"❌ **__Duration Error__**\n\n**Allowed Duration:** `{DURATION_LIMIT}` minute(s)\n**Received Duration:** `{duration}` minute(s)"
            )
        file_name = (
            audio.file_unique_id
            + "."
            + (
                (audio.file_name.split(".")[-1])
                if (not isinstance(audio, Voice))
                else "ogg"
            )
        )
        file_name = path.join(path.realpath("downloads"), file_name)
        file = await convert(
            (await message.reply_to_message.download(file_name))
            if (not path.isfile(file_name))
            else file_name,
        )

        num = message.reply_to_message
        if num.audio:
            title = audio.title
        elif num.voice:
            title = "telegram audio"
        link = message.reply_to_message.link
        videoid = "smex1"
        message.chat.title
        if len(message.chat.title) > 10:
            ctitle = message.chat.title[:10] + "..."
        else:
            ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        duration = convert_seconds(audio.duration)
        thumb = await gen_thumb(videoid)

    elif url:
        query = " ".join(message.command[1:])
        mystic = await _.send_message(chat_id, "🔍 **Searching the song...**")
        try:
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                link = result["link"]
                videoid = result["id"]
        except Exception as e:
            return await mystic.edit_text(f"Song not found.\n\n**Reason:** {e}")
        smex = int(time_to_seconds(duration))
        if smex > DURATION_LIMIT:
            return await mystic.edit_text(
                f"❌ **__Duration Error__**\n\n**Allowed Duration:** `{DURATION_LIMIT}` minute(s)\n**Received Duration:** `{duration}` minute(s)"
            )
        if duration == "None":
            return await mystic.edit_text("❌ Live stream not supported")
        if views == "None":
            return await mystic.edit_text("❌ Live stream not supported")
        semxbabes = f"Downloading: {title[:55]}"
        await mystic.edit(semxbabes)
        ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        thumb = await gen_thumb(videoid)

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
                    f"**Downloaded {title[:55]}...**\n\n**Size:** `{size}` | **Time:** `{taken}` sec\n\n**Converting file** [__FFmpeg Process__]"
                )
                print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")

        loop = asyncio.get_event_loop()
        x = await loop.run_in_executor(None, download, link, my_hook)
        file = await convert(x)

    else:
        if len(message.command) < 2:
            message.from_user.first_name
            await app.send_message(
                chat_id,
                "**❌ Song not found.** Please provide a correct song title.",
            )
            return
        what = "Query Given"
        await LOG_CHAT(message, what)
        query = message.text.split(None, 1)[1]
        mystic = await app.send_message(chat_id, "🔍 **Searching the song...**")
        try:
            a = VideosSearch(query, limit=5)
            result = (a.result()).get("result")
            title1 = result[0]["title"]
            duration1 = result[0]["duration"]
            title2 = result[1]["title"]
            duration2 = result[1]["duration"]
            title3 = result[2]["title"]
            duration3 = result[2]["duration"]
            title4 = result[3]["title"]
            duration4 = result[3]["duration"]
            title5 = result[4]["title"]
            duration5 = result[4]["duration"]
            ID1 = result[0]["id"]
            ID2 = result[1]["id"]
            ID3 = result[2]["id"]
            ID4 = result[3]["id"]
            ID5 = result[4]["id"]
        except Exception as e:
            return await mystic.edit_text(
                f"😕 Sorry, we couldn't find the song you were looking for\n\n• Check that the name is correct or try by searching the artist.",
                reply_markup=close_keyboard,
            )
        url = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(
            ID1,
            ID2,
            ID3,
            ID4,
            ID5,
            duration1,
            duration2,
            duration3,
            duration4,
            duration5,
            user_id,
            query,
        )
        await mystic.edit(
            f"❓ Choose Your song:\n\n1️⃣ <b>[{title1[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n └ ⚡ __Powered by {BOT_NAME}__\n\n2️⃣ <b>[{title2[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n └ ⚡ __Powered by {BOT_NAME}__\n\n3️⃣ <b>[{title3[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n └ ⚡ __Powered by {BOT_NAME}__\n\n4️⃣ <b>[{title4[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n └ ⚡ __Powered by {BOT_NAME}__\n\n5️⃣ <b>[{title5[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID5})\n └ ⚡ __Powered by {BOT_NAME}__",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
        return
    if await is_active_chat(chat_id):
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await pytgcalls.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=AUTO_END_TIME)
        position = await put(chat_id, file=file)
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        cpl = f"downloads/{_chat_}final.png"
        shutil.copyfile(thumb, cpl)
        f20 = open(f"search/{_chat_}title.txt", "w")
        f20.write(f"{title}")
        f20.close()
        f111 = open(f"search/{_chat_}duration.txt", "w")
        f111.write(f"{duration}")
        f111.close()
        f27 = open(f"search/{_chat_}username.txt", "w")
        f27.write(f"{checking}")
        f27.close()
        if fucksemx != 1:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = audio_markup(videoid, user_id)
        checking = (
            f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )
        await mystic.delete()
        await app.send_photo(
            chat_id,
            photo=thumb,
            caption=(
                f"💡 **Track added to queue »** {position}\n\n🏷️ **Name:** [{title[:35]}...]({link}) \n⏱ **Duration:** `{duration}` \n🎧 **Request by:** {checking}"
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        await mystic.delete()
        lagu = await app.send_photo(
            chat_id,
            photo=thumb,
            caption=(
                f"🏷️ **Name:** [{title[:95]}]({link})\n⏱ Duration: `{duration}`\n💡 Status: `Joining..`\n🎧 Request by:** {checking}"
            ),
            reply_markup=close_keyboard,
        )
        try:
            await music_on(chat_id)
            await yukki.pytgcalls.join_group_call(
                chat_id,
                InputStream(
                    InputAudioStream(
                        file,
                    ),
                ),
                stream_type=StreamType().pulse_stream,
            )
        except Exception as e:
            await asyncio.sleep(4)
            await lagu.delete()
            await app.send_message(chat_id, f"Error: `{e}`")
            return
        except (NoActiveGroupCall, GroupCallNotFound):
            return await app.send_message(
                chat_id,
                "😕 Sorry, no active video chat!\n\n• To use me start the voice chat first",
                reply_markup=close_keyboard,
            )
        await add_active_chat(chat_id)
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        checking = (
            f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
        )
        if fucksemx != 1:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = play_markup(videoid, user_id)
        else:
            f28 = open(f"search/{_chat_}videoid.txt", "w")
            f28.write(f"{videoid}")
            f28.close()
            buttons = audio_markup(videoid, user_id)
        await lagu.edit(
            f"🏷️ **Name:** [{title[:95]}]({link})\n⏱ Duration: `{duration}`\n💡 Status: `Playing`\n🎧 Request by:** {checking}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@app.on_message(command(["vplay", f"vplay@{BOT_USERNAME}"]) & filters.group)
async def vplay(c: Client, message: Message):
    replied = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Support", url=f"https://t.me/{GROUP}"),
                InlineKeyboardButton("Updates", url=f"https://t.me/{CHANNEL}"),
            ]
        ]
    )
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    if not MUST_JOIN:  # Not compulsory
        return
    try:
        try:
            await app.get_chat_member(MUST_JOIN, message.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await app.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await message.reply(
                    f"**Halo {rpk} Untuk menghindari penggunaan yang berlebihan bot ini di khususkan untuk yang sudah join di channel kami!**",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("✨ Join Channel ✨", url=link)]]
                    ),
                )
                await message.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"Masukkan SI ANJING ke dalam @{MUST_JOIN} dan jadikan admin")
    if message.sender_chat:
        return await app.send_message(
            chat_id,
            "You're an __Anonymous__ Admin !\n\n» Revert back to user account from admin rights.",
        )
    try:
        aing = await c.get_me()
    except Exception as e:
        return await app.send_message(chat_id, f"Error: `{e}`")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await app.send_message(
            chat_id,
            f"💡 To use me, I need to be an Administrator with the following permissions:\n\n» ❌ __Delete messages__\n» ❌ __Add users__\n» ❌ __Manage video chat__\n\nData is **updated** automatically after you **promote me**",
        )
        return
    if not a.can_manage_voice_chats:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Manage Video Chats__\n\nOnce done, try again.",
        )
        return
    if not a.can_delete_messages:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Delete Messages__\n\nOnce done, try again.",
        )
        return
    if not a.can_invite_users:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Invite Users via Link__\n\nOnce done, try again.",
        )
        return
    if not a.can_restrict_members:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Ban Users__\n\nOnce done, try again.",
        )
        return
    if not a.can_promote_members:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Add New Admins__\n\nOnce done, try again.",
        )
        return
    if not a.can_pin_messages:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Pin Messages__\n\nOnce done, try again.",
        )
        return
    if not a.can_change_info:
        await app.send_message(
            chat_id,
            "💡 To use me, Give me the following permission below:"
            + "\n\n» ❌ __Can Change Group Info__\n\nOnce done, try again.",
        )
        return
    try:
        ubot = await ASS_ACC.get_me()
        b = await app.get_chat_member(message.chat.id, ubot.id)
        if b.status == "kicked" or b.status == "banned":
            await app.unban_chat_member(message.chat.id, ubot.id)
            invite_link = await app.export_chat_invite_link(message.chat.id)
            if "+" in invite_link:
                invite = (invite_link.replace("+", "")).split("t.me/")[1]
                link_invite = f"https://t.me/joinchat/{invite}"
            await ASS_ACC.join_chat(link_invite)
            await app.promote_chat_member(
                message.chat.id,
                ASSID,
                can_manage_voice_chats=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_pin_messages=True,
                can_change_info=True,
            )
    except UserNotParticipant:
        try:
            invite_link = await app.export_chat_invite_link(message.chat.id)
            if "+" in invite_link:
                invite = (invite_link.replace("+", "")).split("t.me/")[1]
                link_invite = f"https://t.me/joinchat/{invite}"
            await ASS_ACC.join_chat(link_invite)
            await app.promote_chat_member(
                message.chat.id,
                ASSID,
                can_manage_voice_chats=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_pin_messages=True,
                can_change_info=True,
            )
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            return await app.send_message(
                chat_id,
                f"❌ **An error when {ASSNAME} joining**\n\n**Reason**:`{e}`",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🗑️ Close", callback_data="close")]]
                ),
            )

    replied = message.reply_to_message
    url = get_url(message)
    if replied:
        if replied.video or replied.document:
            what = "Video or Document Format"
            await LOG_CHAT(message, what)
            loser = await replied.reply("📥 **Downloading the video...**")
            dl = await replied.download()
            link = replied.link
            if len(message.command) < 2:
                Q = 720
            else:
                pq = message.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await loser.edit(
                        "» **Only 720, 480, 360 allowed** \n💡 **Now Streaming Video In 720P**"
                    )
            try:
                if replied.video:
                    title = replied.video.file_name[:70]
                    duration = replied.video.duration
                elif replied.document:
                    title = replied.document.file_name[:70]
                    duration = replied.document.duration
            except BaseException:
                pass
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, title, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                await app.send_message(
                    chat_id,
                    f"""
💡 **Track added to queue**

🏷 **Name:** [{title[:999]}]({link})
⏱️ **Duration:** `{duration}`
🎧 **Request by:** `{requester}`

#️⃣ **Queue Position** `{pos}`
""",
                    disable_web_page_preview=True,
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                if await is_active_chat(chat_id):
                    try:
                        clear(chat_id)
                    except QueueEmpty:
                        pass
                    await remove_active_chat(chat_id)
                    await yukki.pytgcalls.leave_group_call(chat_id)
                await yukki.pytgcalls.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        dl,
                        HighQualityAudio(),
                        amaze,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, title, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                await app.send_message(
                    chat_id,
                    f"""
▷ **Started video streaming**

🏷 **Name:** [{title[:999]}]({link})
⏱️ **Duration:** `{duration}`
🎧 **Request by:** {requester}

💬 **Playing on:** {message.chat.title}
""",
                    disable_web_page_preview=True,
                    reply_markup=keyboard,
                )

    elif url:
        what = "URL Vplay"
        await LOG_CHAT(message, what)
        query = message.text.split(None, 1)[1]
        kz = await app.send_message(chat_id, "**Processing the url...**")
        try:
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = result["title"]
                duration = result["duration"]
                thumbnail = f"https://i.ytimg.com/vi/{result['id']}/hqdefault.jpg"
                url = result["link"]
                (result["id"])
                result["id"]
        except Exception as e:
            return await kz.edit_text(f"Song not found.\n**Posible reason:** `{e}`")
        Q = 360
        amaze = HighQualityVideo()
        theme = random.choice(themes)
        srrf = message.chat.title
        ctitle = await CHAT_TITLE(srrf)
        userid = message.from_user.id
        z, ytlink = await ytdl(url)
        if z == 0:
            await CallbackQuery.app.send_message(
                chat_id, f"❌ yt-dl problem detected\n\n» `{ytlink}`"
            )
        else:
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, title, ytlink, url, "Video", Q)
                requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                await app.send_message(
                    chat_id,
                    f"""
💡 **Track added to queue**

🏷 **Name:** [{title[:999]}]({url})
⏱️ **Duration:** `{duration}`
🎧 **Request by:** {requester}

#️⃣ **Queue Position** `{pos}`
""",
                    disable_web_page_preview=True,
                    reply_markup=keyboard,
                )
            else:
                try:
                    if await is_active_chat(chat_id):
                        try:
                            clear(chat_id)
                        except QueueEmpty:
                            pass
                        await remove_active_chat(chat_id)
                        await yukki.pytgcalls.leave_group_call(chat_id)
                    await yukki.pytgcalls.join_group_call(
                        chat_id,
                        AudioVideoPiped(
                            ytlink,
                            HighQualityAudio(),
                            amaze,
                        ),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, title, ytlink, url, "Video", Q)
                    await kz.delete()
                    requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                    await app.send_message(
                        chat_id,
                        f"""
▷ **Started video streaming**

🏷 **Name:** [{title[:999]}]({url})
⏱️ **Duration:** `{duration}`
🎧 **Request by:** {requester}

💬 **Playing on:** {message.chat.title}
""",
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                    )
                except Exception as e:
                    await app.send_message(chat_id, f"Error: `{e}`")

    else:
        if len(message.command) < 2:
            await app.send_message(
                chat_id,
                "❌ Video not found.** Please provide a correct video title.",
            )
        else:
            what = "Command Vplay"
            await LOG_CHAT(message, what)
            loser = await app.send_message(chat_id, "**🔎 Searching the video...**")
            query = message.text.split(None, 1)[1]
            Q = 360
            amaze = LowQualityVideo()
            try:
                result = VideosSearch(query, limit=5).result()
                data = result["result"]
            except BaseException:
                await loser.edit("**You did not provide any song titles!**")
            # kontol kalian
            try:
                toxxt = f"**❓ Choose Your song**\n\n"
                j = 0

                emojilist = [
                    "1️⃣",
                    "2️⃣",
                    "3️⃣",
                    "4️⃣",
                    "5️⃣",
                ]
                while j < 5:
                    toxxt += f"{emojilist[j]} **[{data[j]['title'][:25]}...]({data[j]['link']})**\n"
                    toxxt += f"├ 💡 __[More Information](https://t.me/{BOT_USERNAME}?start=info_{data[j]['id']})__\n"
                    toxxt += f"└ ⚡ __Powered by: {BOT_NAME}__\n\n"
                    j += 1
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "1️⃣", callback_data=f"plll 0|{query}|{user_id}"
                            ),
                            InlineKeyboardButton(
                                "2️⃣", callback_data=f"plll 1|{query}|{user_id}"
                            ),
                            InlineKeyboardButton(
                                "3️⃣", callback_data=f"plll 2|{query}|{user_id}"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "4️⃣", callback_data=f"plll 3|{query}|{user_id}"
                            ),
                            InlineKeyboardButton(
                                "5️⃣", callback_data=f"plll 4|{query}|{user_id}"
                            ),
                        ],
                        [InlineKeyboardButton("• Cʟᴏsᴇ", callback_data="cls")],
                    ]
                )
                await app.send_message(
                    chat_id, toxxt, disable_web_page_preview=True, reply_markup=key
                )

                await loser.delete()
                # kontol
                return
                # kontol
            except Exception as e:
                await loser.edit(f"**❌ Error:** `{e}`")
                return
            try:
                songname = data["title"]
                url = data["link"]
                duration = data["duration"]
                thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
                data["id"]
            except BaseException:
                await loser.edit(
                    "❌ Video not found.** Please provide a correct song title."
                )
            theme = random.choice(themes)
            srrf = message.chat.title
            ctitle = await CHAT_TITLE(srrf)
            userid = message.from_user.id
            thumb = await gen_thumb(videoid)
            ytlink = await ytdl(url)
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                await loser.delete()
                requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                await app.send_message(
                    chat_id,
                    f"""
💡 **Track added to queue**

🏷 **Name:** [{songname[:999]}]({url})
⏱️ **Duration:** `{duration}`
🎧 **Request by:** {requester}

#️⃣ **Queue Position** `{pos}`
""",
                    disable_web_page_preview=True,
                    reply_markup=keyboard,
                )
            else:
                try:
                    if await is_active_chat(chat_id):
                        try:
                            clear(chat_id)
                        except QueueEmpty:
                            pass
                        await remove_active_chat(chat_id)
                        await music.pytgcalls.leave_group_call(chat_id)
                    await music.pytgcalls.join_group_call(
                        chat_id,
                        AudioVideoPiped(
                            ytlink,
                            HighQualityAudio(),
                            amaze,
                        ),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, title, ytlink, url, "Video", Q)
                    await loser.delete()
                    requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                    await app.send_message(
                        chat_id,
                        f"""
▷ **Started video streaming**

🏷 **Name:** [{songname[:999]}]({url})
⏱️ **Duration:** {duration}
🎧 **Request by:** {requester}

💬 **Playing on:** {message.chat.title}
""",
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                    )
                except Exception as ep:
                    await loser.delete()
                    await app.send_message(chat_id, f"Error: `{ep}`")


@Client.on_callback_query(filters.regex(pattern=r"plll"))
async def kontol(_, CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Support", url=f"https://t.me/punyazein"),
                InlineKeyboardButton("Updates", url=f"https://t.me/zeinproject"),
            ]
        ]
    )
    chat_id = CallbackQuery.message.chat.id
    callback_data = CallbackQuery.data.strip()
    CallbackQuery.message.chat.title
    callback_request = callback_data.split(None, 1)[1]
    try:
        x, query, user_id = callback_request.split("|")
    except Exception as e:
        await CallbackQuery.app.send_message(chat_id, f"**Error:** `{e}`")
        return
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "💡 Sorry this not your request", show_alert=True
        )
    await CallbackQuery.message.delete()
    requester = f"[{CallbackQuery.from_user.first_name}](tg://user?id={CallbackQuery.from_user.id})"
    x = int(x)
    Q = 360
    amaze = HighQualityVideo()
    a = VideosSearch(query, limit=5)
    data = (a.result()).get("result")
    songname = data[x]["title"]
    data[x]["id"]
    duration = data[x]["duration"]
    url = f"https://www.youtube.com/watch?v={data[x]['id']}"
    kz, ytlink = await ytdl(url)
    if kz == 0:
        await CallbackQuery.app.send_message(
            chat_id, f"❌ Yt-dl problem detected\n\n» `{ytlink}`"
        )
    else:
        if chat_id in QUEUE:
            pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
            await app.send_message(
                chat_id,
                f"""
💡 **Track added to queue**

🏷 **Name:** [{songname[:999]}]({url})
⏱️ **Duration:** `{duration}`
🎧 **Request by:** {requester}

#️⃣ **Queue Position** `{pos}`
""",
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )
            await CallbackQuery.message.delete()
        else:
            try:
                if await is_active_chat(chat_id):
                    try:
                        clear(chat_id)
                    except QueueEmpty:
                        pass
                    await remove_active_chat(chat_id)
                    await yukki.pytgcalls.leave_group_call(chat_id)
                await yukki.pytgcalls.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        ytlink,
                        HighQualityAudio(),
                        amaze,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                await app.send_message(
                    chat_id,
                    f"""
▷ **Started video streaming**

🏷 **Name:** [{songname[:999]}]({url})
⏱️ **Duration:** {duration}
🎧 **Request by:** {requester}

💬 **Playing on:** {CallbackQuery.message.chat.title}
""",
                    disable_web_page_preview=True,
                    reply_markup=keyboard,
                )
            except Exception as e:
                await CallbackQuery.app.send_message(chat_id, f"**Error:** `{e}`")


@Client.on_callback_query(filters.regex(pattern=r"yukki"))
async def startyuplay(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    try:
        id, duration, user_id = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(f"An error occured\n\n**Reason**:{e}")
    if duration == "None":
        return await CallbackQuery.answer(
            "❌ Live stream not supported", show_alert=True
        )
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "💡 Sorry this not your request", show_alert=True
        )
    await CallbackQuery.message.delete()
    checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    url = f"https://www.youtube.com/watch?v={id}"
    videoid = id
    smex = int(time_to_seconds(duration))
    if smex > DURATION_LIMIT:
        await app.send_message(
            chat_id,
            f"❌ **__Duration Error__**\n\n**Allowed Duration:** `{DURATION_LIMIT}` minute(s)\n**Received Duration:** `{duration}` minute(s)",
        )
        return
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            x = ytdl.extract_info(url, download=False)
    except Exception as e:
        return await app.send_message(
            chat_id, f"❌ Failed to download video.\n\n**Reason**: `{e}`"
        )
    title = x["title"]
    mystic = await app.send_message(chat_id, f"Downloading: {title[:55]}")
    thumbnail = x["thumbnail"]
    videoid = x["id"]

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
                f"**Downloaded: {title[:55]}...**\n\n**Size:** `{size}` | **Time:** `{taken}` sec\n\n**Converting file [__FFmpeg Process__]"
            )
            print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")

    loop = asyncio.get_event_loop()
    x = await loop.run_in_executor(None, download, url, my_hook)
    file = await convert(x)
    ctitle = CallbackQuery.message.chat.title
    ctitle = await CHAT_TITLE(ctitle)
    thumb = await gen_thumb(videoid)
    await mystic.delete()
    if await is_active_chat(chat_id):
        position = await put(chat_id, file=file)
        buttons = play_markup(videoid, user_id)
        _chat_ = (str(file)).replace("_", "", 1).replace("/", "", 1).replace(".", "", 1)
        cpl = f"downloads/{_chat_}final.png"
        shutil.copyfile(thumb, cpl)
        f20 = open(f"search/{_chat_}title.txt", "w")
        f20.write(f"{title}")
        f20.close()
        f111 = open(f"search/{_chat_}duration.txt", "w")
        f111.write(f"{duration}")
        f111.close()
        f27 = open(f"search/{_chat_}username.txt", "w")
        f27.write(f"{checking}")
        f27.close()
        f28 = open(f"search/{_chat_}videoid.txt", "w")
        f28.write(f"{videoid}")
        f28.close()
        await mystic.delete()
        await app.send_photo(
            chat_id,
            photo=thumb,
            caption=(
                f"💡 **Track added to queue »** `{position}`\n\n🏷️ **Name:** [{title[:35]}...]({url})\n⏱ **Duration:** `{duration}`\n🎧 **Request by:** {checking}"
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        os.remove(thumb)
        await CallbackQuery.message.delete()
    else:
        await CallbackQuery.message.delete()
        await mystic.delete()
        memeks = await app.send_photo(
            chat_id,
            photo=thumb,
            caption=f"🏷️ **Name:** [{title[:95]}]({url}) \n⏱ **Duration:** `{duration}`\n💡 **Status:** `Joining...`\n🎧 **Request by:** {checking}",
            reply_markup=close_keyboard,
        )
        try:
            await music_on(chat_id)
            await yukki.pytgcalls.join_group_call(
                chat_id,
                InputStream(
                    InputAudioStream(
                        file,
                    ),
                ),
                stream_type=StreamType().pulse_stream,
            )
        except (NoActiveGroupCall, GroupCallNotFound):
            return await app.send_message(
                chat_id,
                "😕 Sorry, no active video chat!\n\n• To use me start the voice chat first",
                reply_markup=close_keyboard,
            )
        await add_active_chat(chat_id)
        buttons = play_markup(videoid, user_id)
        await memeks.edit(
            f"🏷️ **Name:** [{title[:95]}]({url}) \n⏱ **Duration:** `{duration}`\n💡 **Status:** `Playing`\n🎧 **Request by:** {checking}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        os.remove(thumb)


@Client.on_callback_query(filters.regex(pattern=r"popat"))
async def popat(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    print(callback_request)
    try:
        id, query, user_id = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(f"An error occured\n\n**Reason**: {e}")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "💡 Sorry this not your request", show_alert=True
        )
    i = int(id)
    query = str(query)
    try:
        a = VideosSearch(query, limit=10)
        result = (a.result()).get("result")
        title1 = result[0]["title"]
        duration1 = result[0]["duration"]
        title2 = result[1]["title"]
        duration2 = result[1]["duration"]
        title3 = result[2]["title"]
        duration3 = result[2]["duration"]
        title4 = result[3]["title"]
        duration4 = result[3]["duration"]
        title5 = result[4]["title"]
        duration5 = result[4]["duration"]
        title6 = result[5]["title"]
        duration6 = result[5]["duration"]
        title7 = result[6]["title"]
        duration7 = result[6]["duration"]
        title8 = result[7]["title"]
        duration8 = result[7]["duration"]
        title9 = result[8]["title"]
        duration9 = result[8]["duration"]
        title10 = result[9]["title"]
        duration10 = result[9]["duration"]
        ID1 = result[0]["id"]
        ID2 = result[1]["id"]
        ID3 = result[2]["id"]
        ID4 = result[3]["id"]
        ID5 = result[4]["id"]
        ID6 = result[5]["id"]
        ID7 = result[6]["id"]
        ID8 = result[7]["id"]
        ID9 = result[8]["id"]
        ID10 = result[9]["id"]
    except Exception:
        return await mystic.edit_text(
            "😕 Sorry, we couldn't find the song you were looking for\n\n• Check that the name is correct or try by searching the artist.",
            reply_markup=close_keyboard,
        )
    if i == 1:
        url = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup2(
            ID6,
            ID7,
            ID8,
            ID9,
            ID10,
            duration6,
            duration7,
            duration8,
            duration9,
            duration10,
            user_id,
            query,
        )
        await CallbackQuery.edit_message_text(
            f"❓ Choose Your song:\n\n6️⃣ <b>[{title6[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID6})\n └ ⚡ __Powered by {BOT_NAME}__\n\n7️⃣ <b>[{title7[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID7})\n └ ⚡ __Powered by {BOT_NAME}__\n\n8️⃣ <b>[{title8[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID8})\n └ ⚡ __Powered by {BOT_NAME}__\n\n9️⃣ <b>[{title9[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID9})\n └ ⚡ __Powered by {BOT_NAME}__\n\n🔟 <b>[{title10[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID10})\n └ ⚡ __Powered by {BOT_NAME}__",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
        return
    if i == 2:
        url = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(
            ID1,
            ID2,
            ID3,
            ID4,
            ID5,
            duration1,
            duration2,
            duration3,
            duration4,
            duration5,
            user_id,
            query,
        )
        await CallbackQuery.edit_message_text(
            f"❓ Choose Your song:\n\n1️⃣ <b>[{title1[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n └ ⚡ __Powered by {BOT_NAME}__\n\n2️⃣ <b>[{title2[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n └ ⚡ __Powered by {BOT_NAME}__\n\n3️⃣ <b>[{title3[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n └ ⚡ __Powered by {BOT_NAME}__\n\n4️⃣ <b>[{title4[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n └ ⚡ __Powered by {BOT_NAME}__\n\n5️⃣ <b>[{title5[:28]}...]({url})</b>\n ├ 💡 [More information](https://t.me/{BOT_USERNAME}?start=info_{ID5})\n └ ⚡ __Powered by {BOT_NAME}__",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
        return


@app.on_message(filters.command(["queue", f"queue@{BOT_USERNAME}"]))
async def queue(_, message: Message):
    chat_id = message.chat.id
    global get_queue
    if await is_active_chat(message.chat.id):
        mystic = await app.send_message(chat_id, "Please Wait... Getting Queue..")
        dur_left = db_mem[message.chat.id]["left"]
        duration_min = db_mem[message.chat.id]["total"]
        got_queue = get_queue.get(message.chat.id)
        if not got_queue:
            await mystic.edit(f"Nothing in Queue")
        fetched = []
        for get in got_queue:
            fetched.append(get)

        ### Results
        current_playing = fetched[0][0]
        user_name = fetched[0][1]

        msg = "**Queued List**\n\n"
        msg += "**Currently Playing:**"
        msg += "\n▶️" + current_playing[:30]
        msg += f"\n   ╚ By: {user_name}"
        msg += f"\n   ╚ Duration: Remaining `{dur_left}` out of `{duration_min}` Mins."
        fetched.pop(0)
        if fetched:
            msg += "\n\n"
            msg += "**Up Next In Queue:**"
            for song in fetched:
                name = song[0][:30]
                usr = song[1]
                dur = song[2]
                msg += f"\n⏸️ {name}"
                msg += f"\n   ╠ Duration : {dur}"
                msg += f"\n   ╚ Requested by : {usr}\n"
        if len(msg) > 4096:
            await mystic.delete()
            filename = "queue.txt"
            with open(filename, "w+", encoding="utf8") as out_file:
                out_file.write(str(msg.strip()))
            await app.send_document(
                chat_id,
                document=filename,
                caption=f"**OUTPUT:**\n\n`Queued List`",
                quote=False,
            )
            os.remove(filename)
        else:
            await mystic.edit(msg)
    else:
        await app.send_message(chat_id, f"Nothing in Queue")


@Client.on_message(
    command(["playplaylist", f"playplaylist@{BOT_USERNAME}"]) & other_filters
)
async def play_playlist_cmd(_, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    buttons = playlist_markup(user_name, user_id)
    await app.send_message(
        chat_id,
        "❓ Which playlist do you want to play ?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return


@app.on_message(command(["vplaylist", f"vplaylist@{BOT_USERNAME}"]) & filters.group)
async def playlist(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await m.delete()
            await app.send_message(
                chat_id,
                f"**🎧 NOW PLAYING:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",
                disable_web_page_preview=True,
            )
        else:
            QUE = f"**🎧 NOW PLAYING:** \n[{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}` \n\n**⏯ QUEUED TRACK:**"
            l = len(chat_queue)
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                QUE = QUE + "\n" + f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`\n"
            await app.send_message(chat_id, QUE, disable_web_page_preview=True)
    else:
        await app.send_message(chat_id, "**❌ Nothing in queued**")
