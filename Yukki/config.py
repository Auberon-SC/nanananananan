from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

admins = {}
get_queue = {}

load_dotenv()

BANNED_USERS = filters.user()
YTDOWNLOADER = 1
LOG = 2
LOG_FILE_NAME = "Fumikalogs.txt"
adminlist = {}
lyrical = {}
chatstats = {}
userstats = {}
clean = {}

autoclean = []

SESSION_NAME = getenv("SESSION_NAME", "session")
BOT_TOKEN = getenv("BOT_TOKEN")
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "54000"))
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! .").split())
MONGO_DB_URI = getenv("MONGO_DB_URI")
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "").split()))
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "-1001662591986"))
LOG_GROUP_ID_2 = int(getenv("LOG_GROUP_ID_2", "-1001339411100"))
ASS_ID = int(getenv("ASS_ID", "1906953793"))
OWNER_ID = list(map(int, getenv("OWNER_ID", "").split()))
GROUP = getenv("GROUP", None)
CHANNEL = getenv("CHANNEL", None)
AUTO_LEAVE = int(getenv("AUTO_LEAVE", "2000"))
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/aryazakari01/GroupMusicBot")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", None)
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "5400"))
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)
YOUTUBE_IMG_URL = getenv(
    "YOUTUBE_IMG_URL",
    "cache/audio.png",
)
