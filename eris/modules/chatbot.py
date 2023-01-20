import html
import json
import re
from time import sleep

import requests
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html

import eris.modules.sql.chatbot_sql as sql
from eris import dispatcher
from eris.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from eris.modules.helper_funcs.filters import CustomFilters
from eris.modules.log_channel import gloggable


@run_async
@user_admin_no_reply
@gloggable
def erisrm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_eris = sql.set_eris(chat.id)
        if is_eris:
            is_eris = sql.set_eris(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_DISABLED\n"
                f"<b>Admin :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text("Chatbot has been disabled for this chat.")

    return ""


@run_async
@user_admin_no_reply
@gloggable
def erisadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_eris = sql.rem_eris(chat.id)
        if is_eris:
            is_eris = sql.rem_eris(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_ENABLE\n"
                f"<b>Admin :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text("Chatbot has been enabled for this chat.")

    return ""


@run_async
@user_admin
@gloggable
def eris(update: Update, context: CallbackContext):
    message = update.effective_message
    msg = "Choose an option below"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ENABLE", callback_data="add_chat({})"),
                InlineKeyboardButton(text="DISABLE", callback_data="rm_chat({})"),
            ],
        ]
    )
    message.reply_text(
        text=msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


def eris_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "Eris":
        return True
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False

def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_eris = sql.is_eris(chat_id)
    if is_eris:
        return

    if message.text and not message.document:
        if not eris_message(context, message):
            return
        sweetie = message.text
        bot.send_chat_action(chat_id, action="typing")
        url = f"https://kora-api.vercel.app/chatbot/2d94e37d-937f-4d28-9196-bd5552cac68b/ErisBot/Soumyabrata/message={sweetie}"
        request = requests.get(url)
        results = json.loads(request.text)
        sleep(0.5)
        message.reply_text(f"{results['reply']}")


__mod_name__ = "Chatbot"

__help__ = """
Chatbot helps Eris to talk and communicate with people.
──「 *Commands* 」──
->  `/addchat`
Enables Chatbot mode in the chat.
-> `/rmchat`
Disables Chatbot mode in the chat.
"""

CHATBOTS_HANDLER = CommandHandler("chatbot", eris)
ADD_CHAT_HANDLER = CallbackQueryHandler(erisadd, pattern=r"add_chat")
RM_CHAT_HANDLER = CallbackQueryHandler(erisrm, pattern=r"rm_chat")
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTS_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTS_HANDLER,
    RM_CHAT_HANDLER,
    CHATBOT_HANDLER,
]