from pyrogram import Client
from Yukki.config import API_HASH, API_ID, BOT_TOKEN, SESSION_NAME

app = Client(
    "Music",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
)

userbot = Client(SESSION_NAME, API_ID, API_HASH)
