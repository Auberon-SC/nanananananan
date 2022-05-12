import os

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from Yukki import app, BOT_USERNAME


LOG_GROUPS = os.getenv("LOG_GROUPS", "-1001512154993")


def get_text(message: Message) -> str:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@app.on_message(filters.command(["bug", f"bug@{BOT_USERNAME}"]))
async def bug(_, message: Message):
    chat_id = message.chat.id
    memek = await app.export_chat_invite_link(message.chat.id)
    bugnya = get_text(message)
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    if not bugnya:
        await app.send_message(
            chat_id,
            f"__Give me something to report a bug to my [Support group](https://t.me/punyazein)__",
            disable_web_page_preview=True,
        )
        return
    else:
        await app.send_message(
            chat_id,
            f"✅ [ {bugnya} ] was submitted to support groups. Thanks for reporting the bug.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Close", callback_data="close")]]
            ),
        )
        await app.send_message(
            LOG_GROUPS,
            f"📣 New bug reporting\n\n**Chat:** [{message.chat.title}]({memek})\n**Name:** {mention}\n**User ID:** {message.from_user.id}\n**Username:** @{message.from_user.username}\n\n**Contents of the report:** {bugnya}",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Go To Message", url=f"{message.link}")],
                    [InlineKeyboardButton("Close", callback_data="close")],
                ]
            ),
        )
