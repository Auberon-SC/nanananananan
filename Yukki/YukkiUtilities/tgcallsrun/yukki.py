import os
import asyncio
import yt_dlp

from asyncio import QueueEmpty
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup

from Yukki import config, app
from Yukki.config import LOG_GROUP_ID_2
from Yukki.YukkiUtilities.database.queue import remove_active_chat
from Yukki.YukkiUtilities.helpers.thumbnails import gen_thumb
from Yukki.YukkiUtilities.helpers.chattitle import CHAT_TITLE
from Yukki.YukkiUtilities.helpers.ytdl import ytdl_opts
from Yukki.YukkiUtilities.helpers.inline import play_markup
from Yukki.YukkiUtilities.tgcallsrun import convert, download, queues

flex = {}
smexy = Client(config.SESSION_NAME, config.API_ID, config.API_HASH)
pytgcalls = PyTgCalls(
    smexy,
    cache_duration=100,
    overload_quiet_mode=True,
)


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


@pytgcalls.on_kicked()
async def on_kicked(client: PyTgCalls, chat_id: int) -> None:
    try:
        queues.clear(chat_id)
    except QueueEmpty:
        pass
    await remove_active_chat(chat_id)


@pytgcalls.on_closed_voice_chat()
async def on_closed(client: PyTgCalls, chat_id: int) -> None:
    try:
        queues.clear(chat_id)
    except QueueEmpty:
        pass
    await remove_active_chat(chat_id)


@pytgcalls.on_stream_end()
async def on_stream_end(client: PyTgCalls, update: Update) -> None:
    chat_id = update.chat_id
    try:
        queues.task_done(chat_id)
        if queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await pytgcalls.leave_group_call(chat_id)
        else:
            afk = queues.get(chat_id)["file"]
            f1 = afk[0]
            f2 = afk[1]
            f3 = afk[2]
            finxx = f"{f1}{f2}{f3}"
            if str(finxx) != "raw":
                mystic = await app.send_message(
                    chat_id, "📥 Downloading next music from playlist..."
                )
                url = f"https://www.youtube.com/watch?v={afk}"
                ctitle = (await app.get_chat(chat_id)).title
                logger_text = f"""▶ Playing music from playlist

Group: `{chat_id}`
Title: {ctitle}

🔗 {url}"""
                await smexy.send_message(
                    LOG_GROUP_ID_2, f"{logger_text}", disable_web_page_preview=True
                )
                try:
                    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                        x = ytdl.extract_info(url, download=False)
                except Exception as e:
                    return await mystic.edit(
                        f"Failed to download this video.\n\n**Reason:** {e}"
                    )

                chat_title = ctitle
                videoid = afk
                title = x["title"]

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
                            mystic.edit(
                                f"Downloading {title[:50]}\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}`\n**ETA:** `{eta}` sec"
                            )
                        if per > 500:
                            if flex[str(bytesx)] == 2:
                                flex[str(bytesx)] += 1
                                mystic.edit(
                                    f"Downloading {title[:50]}...\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                )
                                print(
                                    f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds"
                                )
                        if per > 800:
                            if flex[str(bytesx)] == 3:
                                flex[str(bytesx)] += 1
                                mystic.edit(
                                    f"Downloading {title[:50]}....\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                )
                                print(
                                    f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds"
                                )
                        if per == 1000:
                            if flex[str(bytesx)] == 4:
                                flex[str(bytesx)] = 1
                                mystic.edit(
                                    f"Downloading {title[:50]}.....\n\n**Size:** `{size}` | **Downloaded:** `{percentage}`\n\n**Speed:** `{speed}` | **ETA:** `{eta}` sec"
                                )
                                print(
                                    f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds"
                                )

                loop = asyncio.get_event_loop()
                xx = await loop.run_in_executor(None, download, url, my_hook)
                file = await convert(xx)
                await pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            file,
                        ),
                    ),
                )
                duration = convert_seconds(x["duration"] / 60)
                ctitle = await CHAT_TITLE(ctitle)
                f2 = open(f"search/{afk}id.txt", "r")
                userid = f2.read()
                thumb = await gen_thumb(videoid)
                user_id = userid
                videoid = afk
                buttons = play_markup(videoid, user_id)
                await mystic.delete()
                semx = await app.get_users(userid)
                await app.send_photo(
                    chat_id,
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(
                        f"🏷️ **Name:** [{title[:80]}]({url})\n⏱ **Duration:** `{duration}`\n💡 **Status**: `Playing`\n🎧 **Request by:** {semx.mention}"
                    ),
                )
                os.remove(thumb)
            else:
                await pytgcalls.change_stream(
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
                duration = f3.read()
                f4 = open(f"search/{_chat_}username.txt", "r")
                f4 = open(f"search/{_chat_}videoid.txt", "r")
                videoid = f4.read()
                user_id = 1
                videoid = str(videoid)
                return

    except Exception as e:
        print(e)


run = pytgcalls.start
