import psutil
import time

from datetime import datetime
from pyrogram import filters
from Yukki import app, YUKKI_START_TIME
from Yukki.YukkiUtilities.helpers.time import get_readable_time
from Yukki.YukkiUtilities.tgcallsrun.yukki import pytgcalls


async def bot_sys_stats():
    bot_uptime = int(time.time() - YUKKI_START_TIME)
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    stats = f"""
» Uptime: `{get_readable_time((bot_uptime))}`
» CPU: `{cpu}`%
» RAM: `{mem}`%
» Disk: `{disk}`%"""
    return stats


@app.on_message(filters.command(["mping", "mping@RessoStreamBot"]))
async def ping(_, message):
    chat_id = message.chat.id
    pytgping = await pytgcalls.ping
    uptime = await bot_sys_stats()
    start = datetime.now()
    response = await app.send_message(chat_id, "`Pinging`...")
    end = datetime.now()
    resp = (end - start).microseconds / 1000
    await response.edit_text(
        f"PONG!: `{resp}` ms\n\nPytgcalls Latency: `{pytgping}`\n\n🖥 System Stats:\n{uptime}"
    )
