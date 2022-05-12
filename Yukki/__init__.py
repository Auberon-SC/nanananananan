print("[ INFO ] : STARTING CLIENT")

import time
import asyncio

from logging import getLogger
from rich.console import Console
from pyrogram import Client
from pyrogram import Client as Bot
from aiohttp import ClientSession
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from Yukki import config
from Yukki.config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    MONGO_DB_URI,
    UPSTREAM_BRANCH,
    UPSTREAM_REPO,
    SUDO_USERS,
    OWNER_ID,
    CHANNEL,
    GROUP,
)
from Yukki.config import MONGO_DB_URI as mango
from Yukki.converter.cli import app, userbot
from Yukki.YukkiUtilities.helpers.tasks import install_requirements
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient


console = Console()


def initialize():
    global dbb
    dbb = {}


### Mongo DB
MONGODB_CLI = Bot(mango)
db = MONGODB_CLI
pymongodb = ""

### Boot Time
boottime = time.time()

### Clients
app = app
userbot = userbot
aiohttpsession = ClientSession()


initialize()

UPSTREAM_BRANCH = UPSTREAM_BRANCH
UPSTREAM_REPO = UPSTREAM_REPO

print("[ INFO ] : INITIALIZING DATABASE")

LOGS = getLogger(__name__)

__version__ = "4.7.9"

MONGODB_CLI = MongoClient(MONGO_DB_URI)
db = MONGODB_CLI.wbb
SUDOERS = SUDO_USERS
OWNER = OWNER_ID
CHANNEL = CHANNEL
GROUP = GROUP


async def load_sudoers():
    global SUDOERS
    print("[ INFO ] : LOADING SUDO USERS")
    sudoersdb = db.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    for user_id in SUDOERS:
        if user_id not in sudoers:
            sudoers.append(user_id)
            await sudoersdb.update_one(
                {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
            )
    SUDOERS = (SUDOERS + sudoers) if sudoers else SUDOERS
    print("[INFO]: LOADED SUDO USERS")
    try:
        repo = Repo()
    except GitCommandError:
        console.print("┌ [red] Checking Git Updates!")
        console.print("└ [red]Git Command Error\n")
        return
    except InvalidGitRepositoryError:
        console.print("┌ [red] Checking Git Updates!")
        repo = Repo.init()
        if "origin" in repo.remotes:
            origin = repo.remote("origin")
        else:
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head(UPSTREAM_BRANCH, origin.refs[UPSTREAM_BRANCH])
        repo.heads[UPSTREAM_BRANCH].set_tracking_branch(origin.refs[UPSTREAM_BRANCH])
        repo.heads[UPSTREAM_BRANCH].checkout(True)
        try:
            repo.create_remote("origin", UPSTREAM_REPO)
        except BaseException:
            pass
        nrs = repo.remote("origin")
        nrs.fetch(UPSTREAM_BRANCH)
        try:
            nrs.pull(UPSTREAM_BRANCH)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await install_requirements("pip3 install --no-cache-dir -r requirements.txt")
        console.print("└ [red]Git Client Update Completed\n")


loop = asyncio.get_event_loop()
loop.run_until_complete(load_sudoers())
YUKKI_START_TIME = time.time()
loop = asyncio.get_event_loop()


BOT_ID = 0
BOT_NAME = ""
BOT_USERNAME = ""
ASSID = 0
ASSNAME = ""
ASSUSERNAME = ""
ASSMENTION = ""
print("[INFO]: INITIALIZING BOT CLIENT")
app = Client(
    "group",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
)
aiohttpsession = ClientSession()

chacha = Client(config.SESSION_NAME, config.API_ID, config.API_HASH)


def all_info(app, chacha):
    global BOT_ID, BOT_NAME, BOT_USERNAME
    global ASSID, ASSNAME, ASSMENTION, ASSUSERNAME
    getme = app.get_me()
    getme1 = chacha.get_me()
    BOT_ID = getme.id
    ASSID = getme1.id
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name
    BOT_USERNAME = getme.username
    ASSNAME = (
        f"{getme1.first_name} {getme1.last_name}"
        if getme1.last_name
        else getme1.first_name
    )
    ASSUSERNAME = getme1.username
    ASSMENTION = getme1.mention


def init_db():
    global db_mem
    db_mem = {}


init_db()


print("[ INFO ] : STARTING TELEBOT CLIENT")
app.start()
print("[ INFO ] : STARTING USERBOT CLIENT")
chacha.start()
print("[ INFO ] : GENERATING BOT/ASSISTANT PROFILE INFO")
all_info(app, chacha)
print("[ INFO ] : GENERATED BOT/ASSISTANT PROFILE INFO")
