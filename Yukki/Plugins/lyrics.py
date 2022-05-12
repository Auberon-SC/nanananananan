import os
import re
import lyricsgenius

from Yukki import app
from pyrogram.types import Message
from pyrogram import filters
from youtubesearchpython import VideosSearch


@app.on_callback_query(filters.regex(pattern=r"lyrics"))
async def lyrics_data(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    try:
        id = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(f"Error: `{e}`")
    url = f"https://www.youtube.com/watch?v={id}"
    print(url)
    try:
        results = VideosSearch(url, limit=1)
        for result in results.result()["result"]:
            title = result["title"]
    except Exception as e:
        return await CallbackQuery.answer(
            "Song not found due to youtube issue", show_alert=True
        )
    x = "OXaVabSRKQLqwpiYOn-E4Y7k3wj-TNdL5RfDPXlnXhCErbcqVvdCF-WnMR5TBctI"
    y = lyricsgenius.Genius(x)
    t = re.sub(r"[^\w]", " ", title)
    y.verbose = False
    S = y.search_song(t, get_full_info=False)
    if S is None:
        return await CallbackQuery.answer("Sorry lyrics not found", show_alert=True)
    userid = CallbackQuery.from_user.id
    usr = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    xxx = f"""
**Song Name:** __{title}__
**Artist Name:** {S.artist}
**Requested By:** {usr}

**__Lyrics:__**

{S.lyrics}"""
    if len(xxx) > 4096:
        filename = "lyrics.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(xxx.strip()))
        await app.send_document(
            chat_id,
            document=filename,
            caption=f"**OUTPUT:**\n\n`Lyrics`",
            quote=False,
        )
        os.remove(filename)
    else:
        await app.send_message(chat_id, xxx)


@app.on_message(filters.command("lyrics"))
async def lyric_search(_, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await app.send_message(chat_id, "**Usage:**\n\n/lyrics [music name]")
    m = await app.send_message(chat_id, "🔍 Searching lyrics...")
    query = message.text.split(None, 1)[1]
    x = "OXaVabSRKQLqwpiYOn-E4Y7k3wj-TNdL5RfDPXlnXhCErbcqVvdCF-WnMR5TBctI"
    y = lyricsgenius.Genius(x)
    y.verbose = False
    S = y.search_song(query, get_full_info=False)
    if S is None:
        return await m.edit("Sorry lyrics not found")
    xxx = f"""
**Song Name:** __{query}__
**Artist Name:** {S.artist}

**__Lyrics:__**

{S.lyrics}"""
    if len(xxx) > 4096:
        filename = "lyrics.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(xxx.strip()))
        await app.send_document(
            chat_id,
            document=filename,
            caption=f"**OUTPUT:**\n\n`Lyrics`",
            quote=False,
        )
        os.remove(filename)
    else:
        await m.edit(xxx)
