import os
import wget
import speedtest

from PIL import Image
from Yukki import app, SUDOERS
from Yukki.YukkiUtilities.database.onoff import is_on_off
from pyrogram import filters


@app.on_message(filters.command("mspeedtest") & ~filters.edited)
async def run_speedtest(_, message):
    chat_id = message.chat.id
    userid = message.from_user.id
    if await is_on_off(2):
        if userid in SUDOERS:
            pass
        else:
            return
    m = await app.send_message(chat_id, "Starting server test...")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = await m.edit("⚡️ Running download speedtest")
        test.download()
        m = await m.edit("⚡️ Running upload speedtest")
        test.upload()
        test.results.share()
    except speedtest.ShareResultsConnectFailure:
        pass
    except Exception as e:
        await m.edit_text(e)
        return
    result = test.results.dict()
    m = await m.edit_text("🔄 Sharing speedtest results")
    if result["share"]:
        path = wget.download(result["share"])
        try:
            img = Image.open(path)
            c = img.crop((17, 11, 727, 389))
            c.save(path)
        except BaseException:
            pass
    output = f"""💡 **SpeedTest Results**
    
<u>**Client:**</u>

**ISP:** {result['client']['isp']}
**Country:** {result['client']['country']}
  
<u>**Server:**</u>

**Name:** {result['server']['name']}
**Country:** {result['server']['country']}, {result['server']['cc']}
**Sponsor:** {result['server']['sponsor']}
**Latency:** {result['server']['latency']}

⚡ **Ping:** {result['ping']}"""
    if result["share"]:
        msg = await app.send_photo(chat_id=message.chat.id, photo=path, caption=output)
        os.remove(path)
    else:
        msg = await app.send_message(chat_id=message.chat.id, text=output)
    await m.delete()
