from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from Yukki import BOT_NAME, BOT_USERNAME
from Yukki.config import GROUP, CHANNEL


def stream_markup(videoid, user_id):
    buttons = [
        [
            InlineKeyboardButton(text="❌ Cancel", callback_data=f"stopvc2"),
            InlineKeyboardButton(text="• Cʟᴏsᴇ​ •", callback_data=f"close2"),
        ],
    ]
    return buttons


def play_markup(videoid, user_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="• Mᴇɴᴜ​ •", callback_data=f"other {videoid}|{user_id}"
            ),
            InlineKeyboardButton(text="• Cʟᴏsᴇ​ •", callback_data=f"close2"),
        ],
    ]
    return buttons


def others_markup(videoid, user_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="✚ Your Playlist", callback_data=f"playlist {videoid}|{user_id}"
            ),
            InlineKeyboardButton(
                text="✚ Group Playlist",
                callback_data=f"group_playlist {videoid}|{user_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Go Back", callback_data=f"goback {videoid}|{user_id}"
            )
        ],
    ]
    return buttons


play_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("• Cʟᴏsᴇ​ •", callback_data="close")],
    ]
)


def audio_markup(videoid, user_id):
    buttons = [
        [InlineKeyboardButton(text="• Cʟᴏsᴇ •​", callback_data="close2")],
    ]
    return buttons


def search_markup(
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
):
    buttons = [
        [
            InlineKeyboardButton(
                text="1️⃣", callback_data=f"yukki2 {ID1}|{duration1}|{user_id}"
            ),
            InlineKeyboardButton(
                text="2️⃣", callback_data=f"yukki2 {ID2}|{duration2}|{user_id}"
            ),
            InlineKeyboardButton(
                text="3️⃣", callback_data=f"yukki2 {ID3}|{duration3}|{user_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="4️⃣", callback_data=f"yukki2 {ID4}|{duration4}|{user_id}"
            ),
            InlineKeyboardButton(
                text="5️⃣", callback_data=f"yukki2 {ID5}|{duration5}|{user_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="➡", callback_data=f"popat 1|{query[:14]}|{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="• Cʟᴏsᴇ •​", callback_data=f"ppcl2 smex|{user_id}"
            )
        ],
    ]
    return buttons


def search_markup2(
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
):
    buttons = [
        [
            InlineKeyboardButton(
                text="6️⃣", callback_data=f"yukki2 {ID6}|{duration6}|{user_id}"
            ),
            InlineKeyboardButton(
                text="7️⃣", callback_data=f"yukki2 {ID7}|{duration7}|{user_id}"
            ),
            InlineKeyboardButton(
                text="8️⃣", callback_data=f"yukki2 {ID8}|{duration8}|{user_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="9️⃣", callback_data=f"yukki2 {ID9}|{duration9}|{user_id}"
            ),
            InlineKeyboardButton(
                text="🔟", callback_data=f"yukki2 {ID10}|{duration10}|{user_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅", callback_data=f"popat 2|{query[:14]}|{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="• Cʟᴏsᴇ •​", callback_data=f"ppcl2 smex|{user_id}"
            )
        ],
    ]
    return buttons


def personal_markup(link):
    buttons = [
        [InlineKeyboardButton(text="• Cʟᴏsᴇ​ •", callback_data=f"cls")],
    ]
    return buttons


start_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "📚 Commands", url="https://telegra.ph/Veez-Mega-Bot-09-30"
            )
        ],
        [InlineKeyboardButton("• Cʟᴏsᴇ​ •", callback_data="close2")],
    ]
)


confirm_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("✅ Yes", callback_data="cbdel"),
            InlineKeyboardButton("❌ No", callback_data="close2"),
        ]
    ]
)


confirm_group_keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("✅ Yes", callback_data="cbgroupdel"),
            InlineKeyboardButton("❌ No", callback_data="close2"),
        ]
    ]
)


close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("• Cʟᴏsᴇ •​", callback_data="close2")]]
)


none_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("• Cʟᴏsᴇ​ •", callback_data="cls")]]
)


play_list_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Personal Playlist", callback_data="P_list")],
        [InlineKeyboardButton("Group's Playlist", callback_data="G_list")],
        [InlineKeyboardButton("• Cʟᴏsᴇ •​", callback_data="close2")],
    ]
)


def playlist_markup(user_name, user_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"Group's Playlist", callback_data=f"play_playlist {user_id}|group"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{user_name[:8]}'s Playlist",
                callback_data=f"play_playlist {user_id}|personal",
            )
        ],
        [InlineKeyboardButton(text="• Cʟᴏsᴇ •​", callback_data="close2")],
    ]
    return buttons


def start_pannel():
    if not CHANNEL and not GROUP:
        buttons = [
            [InlineKeyboardButton(text="🔧 Settings", callback_data="settingm")],
        ]
        return f"🎛  **This is {BOT_NAME}**", buttons
    if not CHANNEL and GROUP:
        buttons = [
            [InlineKeyboardButton(text="🔧 Settings", callback_data="settingm")],
            [
                InlineKeyboardButton(text="✨ Support", url=f"https://t.me/{GROUP}"),
            ],
        ]
        return f"🎛  **This is {BOT_NAME}*", buttons
    if CHANNEL and not GROUP:
        buttons = [
            [InlineKeyboardButton(text="🔧 Settings", callback_data="settingm")],
            [
                InlineKeyboardButton(text="✨ Channel", url=f"https://t.me/{GROUP}"),
            ],
        ]
        return f"🎛  **This is {BOT_NAME}**", buttons
    if CHANNEL and GROUP:
        buttons = [
            [InlineKeyboardButton(text="🔧 Settings", callback_data="settingm")],
            [
                InlineKeyboardButton(text="✨ Channel", url=f"https://t.me/{CHANNEL}"),
                InlineKeyboardButton(text="✨ Support", url=f"https://t.me/{GROUP}"),
            ],
        ]
        return f"🎛  **This is {BOT_NAME}**", buttons


def private_panel():
    if not CHANNEL and not GROUP:
        buttons = [
            [
                InlineKeyboardButton(
                    "➕ Add Me To Your Groups",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                )
            ],
        ]
        return f"🎛  **This is {BOT_NAME}**", buttons
    if not CHANNEL and GROUP:
        buttons = [
            [
                InlineKeyboardButton(
                    "➕ Add Me To Your Groups",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton(text="✨ Support", url=f"https://t.me/{GROUP}"),
            ],
        ]
        return f"🎛  **This is {BOT_NAME}*", buttons
    if CHANNEL and not GROUP:
        buttons = [
            [
                InlineKeyboardButton(
                    "➕ Add Me To Your Groups",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton(text="✨ Channel", url=f"https://t.me/{GROUP}"),
            ],
        ]
        return f"🎛  **This is {BOT_NAME}**", buttons
    if CHANNEL and GROUP:
        buttons = [
            [
                InlineKeyboardButton(
                    "➕ Add Me To Your Groups",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton(text="✨ Channel", url=f"https://t.me/{CHANNEL}"),
                InlineKeyboardButton(text="✨ Support", url=f"https://t.me/{GROUP}"),
            ],
        ]
        return f"🎛  **This is {BOT_NAME}**", buttons


def setting_markup():
    buttons = [
        [
            InlineKeyboardButton(text="🔈 Audio quality", callback_data="AQ"),
            InlineKeyboardButton(text="🎚 Volume", callback_data="AV"),
        ],
        [
            InlineKeyboardButton(text="📚 Repository", url="https://github.com"),
            InlineKeyboardButton(text="💻 Dashboard", callback_data="Dashboard"),
        ],
        [
            InlineKeyboardButton(text="🧙‍♂️ Authorized users", callback_data="AU"),
            InlineKeyboardButton(text="🇬🇧 Languages", callback_data="languages"),
        ],
        [
            InlineKeyboardButton(text="• Cʟᴏsᴇ​ •", callback_data="close"),
        ],
    ]
    return f"⚙️ Bot Settings**", buttons


def volmarkup():
    buttons = [
        [InlineKeyboardButton(text="🎛 Preset 🎛", callback_data="HV")],
        [
            InlineKeyboardButton(text="Low", callback_data="LV"),
            InlineKeyboardButton(text="Medium", callback_data="MV"),
        ],
        [
            InlineKeyboardButton(text="High", callback_data="HV"),
            InlineKeyboardButton(text="Amplified", callback_data="VAM"),
        ],
        [InlineKeyboardButton(text="🔽 Custom 🔽", callback_data="Custommarkup")],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="settingm")],
    ]
    return f"⚙️ Bot Settings**", buttons


def custommarkup():
    buttons = [
        [
            InlineKeyboardButton(text="+10", callback_data="PTEN"),
            InlineKeyboardButton(text="-10", callback_data="MTEN"),
        ],
        [
            InlineKeyboardButton(text="+25", callback_data="PTF"),
            InlineKeyboardButton(text="-25", callback_data="MTF"),
        ],
        [
            InlineKeyboardButton(text="+50", callback_data="PFZ"),
            InlineKeyboardButton(text="-50", callback_data="MFZ"),
        ],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="AV")],
    ]
    return f"⚙️ Bot Settings**", buttons


def usermarkup():
    buttons = [
        [
            InlineKeyboardButton(text="👥 Everyone", callback_data="EVE"),
            InlineKeyboardButton(text="🧙‍♂️ Authorizeds", callback_data="AMS"),
        ],
        [
            InlineKeyboardButton(
                text="📋 Authorized users list", callback_data="USERLIST"
            )
        ],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="settingm")],
    ]
    return f"⚙️ Bot Settings**", buttons


def dashmarkup():
    buttons = [
        [
            InlineKeyboardButton(text="✔️ Uptime", callback_data="UPT"),
            InlineKeyboardButton(text="💾 Ram", callback_data="RAT"),
        ],
        [
            InlineKeyboardButton(text="💻 CPU", callback_data="CPT"),
            InlineKeyboardButton(text="💽 Disk", callback_data="DIT"),
        ],
        [InlineKeyboardButton(text="🔙 Go Back", callback_data="settingm")],
    ]
    return f"⚙️ Bot Settings**", buttons


stats1 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="System Stats", callback_data=f"sys_stats"),
            InlineKeyboardButton(text="Storage Stats", callback_data=f"sto_stats"),
        ],
        [
            InlineKeyboardButton(text="Bot Stats", callback_data=f"bot_stats"),
            InlineKeyboardButton(text="Assistant Stats", callback_data=f"assis_stats"),
        ],
    ]
)

stats2 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="General Stats", callback_data=f"gen_stats"),
            InlineKeyboardButton(text="Storage Stats", callback_data=f"sto_stats"),
        ],
        [
            InlineKeyboardButton(text="Bot Stats", callback_data=f"bot_stats"),
            InlineKeyboardButton(text="Assistant Stats", callback_data=f"assis_stats"),
        ],
    ]
)

stats3 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="System Stats", callback_data=f"sys_stats"),
            InlineKeyboardButton(text="General Stats", callback_data=f"gen_stats"),
        ],
        [
            InlineKeyboardButton(text="Bot Stats", callback_data=f"bot_stats"),
            InlineKeyboardButton(text="Assistant Stats", callback_data=f"assis_stats"),
        ],
    ]
)

stats4 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="System Stats", callback_data=f"sys_stats"),
            InlineKeyboardButton(text="Storage Stats", callback_data=f"sto_stats"),
        ],
        [
            InlineKeyboardButton(text="General Stats", callback_data=f"gen_stats"),
            InlineKeyboardButton(text="Assistant Stats", callback_data=f"assis_stats"),
        ],
    ]
)


stats5 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="System Storage", callback_data=f"sys_stats"),
            InlineKeyboardButton(text="Storage Stats", callback_data=f"sto_stats"),
        ],
        [
            InlineKeyboardButton(text="Bot Stats", callback_data=f"bot_stats"),
            InlineKeyboardButton(text="General Stats", callback_data=f"gen_stats"),
        ],
    ]
)


stats6 = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Getting Assistant Stats....",
                callback_data=f"wait_stats",
            )
        ]
    ]
)
