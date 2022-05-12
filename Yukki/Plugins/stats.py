import time
import platform
import psutil

from datetime import datetime
from pyrogram import filters
from sys import version as pyver
from pyrogram import __version__ as pyrover
from pytgcalls import __version__ as pytover

from Yukki import app, SUDOERS, chacha as userbot, boottime, db
from Yukki.Plugins import ALL_MODULES
from Yukki.YukkiUtilities.database.gbanned import get_gbans_count
from Yukki.YukkiUtilities.database.chats import get_served_chats, get_served_users
from Yukki.YukkiUtilities.database.queue import get_queries
from Yukki.YukkiUtilities.database.sudo import get_sudoers, get_sudoers
from Yukki.YukkiUtilities.helpers.inline import (
    stats1,
    stats2,
    stats3,
    stats4,
    stats5,
    stats6,
)
from Yukki.YukkiUtilities.helpers.filters import command
from Yukki.YukkiUtilities.helpers.time import get_readable_time


async def bot_sys_stats():
    bot_uptime = int(time.time() - boottime)
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    stats = f"""
**Uptime:** `{get_readable_time((bot_uptime))}`
**CPU:** `{cpu}`%
**RAM:** `{mem}`%
**Disk:** `{disk}`%"""
    return stats


@app.on_message(command(["mstats", "system"]) & filters.user(SUDOERS))
async def gstats(_, message):
    chat_id = message.chat.id
    start = datetime.now()
    uptime = await bot_sys_stats()
    response = await app.send_message(chat_id, "Getting Stats!")
    end = datetime.now()
    resp = (end - start).microseconds / 1000
    smex = f"""
[•] **General Stats**
    
Ping: ⚡ `{resp}` ms
{uptime}
    """
    await response.edit_text(smex, reply_markup=stats1)
    return


@app.on_callback_query(
    filters.regex(
        pattern=r"^(sys_stats|sto_stats|bot_stats|Dashboard|mongo_stats|gen_stats|assis_stats|wait_stats)$"
    )
)
async def stats_markup(_, CallbackQuery):
    command = CallbackQuery.matches[0].group(1)
    if command == "sys_stats":
        await CallbackQuery.answer("Getting System Stats...", show_alert=True)
        sc = platform.system()
        arch = platform.machine()
        ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
        bot_uptime = int(time.time() - boottime)
        uptime = f"{get_readable_time((bot_uptime))}"
        smex = f"""
[•] **System Stats**

**Uptime:** `{uptime}`
**System Process:** `Online`
**Platform:** `{sc}`
**Architecture:** `{arch}`
**Ram:** `{ram}`
**PyTgCalls Version:** `{pytover.__version__}`
**Python Version:** `{pyver.split()[0]}`
**Pyrogram Version:** `{pyrover}`"""
        await CallbackQuery.edit_message_text(smex, reply_markup=stats2)
    if command == "sto_stats":
        await CallbackQuery.answer("Getting Storage Stats...", show_alert=True)
        hdd = psutil.disk_usage("/")
        total = hdd.total / (1024.0**3)
        total = str(total)
        used = hdd.used / (1024.0**3)
        used = str(used)
        free = hdd.free / (1024.0**3)
        free = str(free)
        smex = f"""
[•] **Storage Stats**

**Storage Available:** `{total[:4]}` GiB 
**Storage Used:** `{used[:4]}` GiB
**Storage Left:** `{free[:4]}` GiB"""
        await CallbackQuery.edit_message_text(smex, reply_markup=stats3)
    if command == "bot_stats":
        await CallbackQuery.answer("Getting Bot Stats...", show_alert=True)
        served_chats = []
        chats = await get_served_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
        blocked = await get_gbans_count()
        sudoers = await get_sudoers()
        modules_loaded = len(ALL_MODULES)
        j = 0
        for user_id in enumerate(sudoers, 0):
            try:
                user = await app.get_users(user_id)
                j += 1
            except Exception:
                continue
        smex = f"""
[•] **Bot Stats**

**Modules Loaded:** `{modules_loaded}`
**GBanned Users:** `{blocked}`
**Sudo Users:** `{j}`
**Served Chats:** `{len(served_chats)}`"""
        await CallbackQuery.edit_message_text(smex, reply_markup=stats4)
    if command == "assis_stats":
        await CallbackQuery.answer("Getting Assistant Stats...", show_alert=True)
        await CallbackQuery.edit_message_text(
            "Getting Assistant Stats.. Please Wait...", reply_markup=stats6
        )
        groups_ub = channels_ub = bots_ub = privates_ub = total_ub = 0
        async for i in userbot.iter_dialogs():
            t = i.chat.type
            total_ub += 1
            if t in ["supergroup", "group"]:
                groups_ub += 1
            elif t == "channel":
                channels_ub += 1
            elif t == "bot":
                bots_ub += 1
            elif t == "private":
                privates_ub += 1

        smex = f"""
[•] **Assistant Stats**

**Dialogs:** `{total_ub}`
**Groups:** `{groups_ub}`
**Channels:** `{channels_ub}`
**Bots:** `{bots_ub}`
**Users:** `{privates_ub}`"""
        await CallbackQuery.edit_message_text(smex, reply_markup=stats5)
    if command == "gen_stats":
        start = datetime.now()
        uptime = await bot_sys_stats()
        await CallbackQuery.answer("Getting General Stats...", show_alert=True)
        end = datetime.now()
        resp = (end - start).microseconds / 1000
        smex = f"""
[•] **General Stats**

**Ping:** ⚡ `{resp}` ms
{uptime}"""
        await CallbackQuery.edit_message_text(smex, reply_markup=stats1)
    if command == "wait_stats":
        await CallbackQuery.answer()
