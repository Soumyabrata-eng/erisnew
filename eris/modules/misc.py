import html
import re
from typing import List
import time

import requests
from telegram import Update, MessageEntity, ParseMode, Chat, User
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async, Filters, CallbackContext
from telegram.utils.helpers import mention_html
from io import BytesIO
from eris import dispatcher, OWNER_ID, DRAGONS, DEMONS, TIGERS, WOLVES, DEV_USERS, INFOPIC
from eris.__main__ import USER_INFO
from eris.modules.disable import DisableAbleCommandHandler
from eris.modules.helper_funcs.chat_status import user_admin, sudo_plus
from eris.modules.helper_funcs.extraction import extract_user
import eris.modules.sql.users_sql as sql

MARKDOWN_HELP = f"""
Markdown is a very powerful formatting tool supported by telegram. {dispatcher.bot.first_name} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>

- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
"""

@run_async
def get_id(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    message = update.effective_message
    msg = update.effective_message
    user_id = extract_user(msg, args)

    if user_id:
        if msg.reply_to_message and msg.reply_to_message.forward_from:

            user1 = message.reply_to_message.from_user
            user2 = message.reply_to_message.forward_from

            msg.reply_text(
                f"The original sender, {html.escape(user2.first_name)},"
                f" has an ID of <code>{user2.id}</code>.\n"
                f"The forwarder, {html.escape(user1.first_name)},"
                f" has an ID of <code>{user1.id}</code>.",
                parse_mode=ParseMode.HTML)

        else:

            user = bot.get_chat(user_id)
            msg.reply_text(
                f"{html.escape(user.first_name)}'s id is <code>{user.id}</code>.",
                parse_mode=ParseMode.HTML)

    else:

        chat = update.effective_chat
        if chat.type == "private":
            msg.reply_text(f"Your id is <code>{chat.id}</code>.",
                        parse_mode=ParseMode.HTML)

        else:
            msg.reply_text(f"This group's id is <code>{chat.id}</code>.",
                        parse_mode=ParseMode.HTML)


@run_async
def gifid(update: Update, _):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        update.effective_message.reply_text(
            f"Gif ID:\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML)
    else:
        update.effective_message.reply_text(
            "Please reply to a gif to get its ID.")



@run_async
def ping(update: Update, _):
    msg = update.effective_message
    start_time = time.time()
    message = msg.reply_text("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 3)
    message.edit_text("*Pong!!!*\n`{}ms`".format(ping_time),
                    parse_mode=ParseMode.MARKDOWN)


@run_async
@user_admin
def echo(update: Update, _):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)

    message.delete()


@run_async
def markdown_help(update: Update, _):
    update.effective_message.reply_text(
        MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see!")
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, `code`, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)")

def info(update: Update, context: CallbackContext): 
    bot = context.bot
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    if user_id := extract_user(update.effective_message, args):
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = (
            message.sender_chat
            if message.sender_chat is not None
            else message.from_user
        )

    elif not message.reply_to_message and (
        not args
        or (
            len(args) >= 1
            and not args[0].startswith("@")
            and not args[0].lstrip("-").isdigit()
            and not message.parse_entities([MessageEntity.TEXT_MENTION])
        )
    ):
        message.reply_text("I can't extract a user from this.")
        return

    else:
        return

    if hasattr(user, 'type') and user.type != "private":
        text = get_chat_info(user)
        is_chat = True
    else:
        text = get_user_info(chat, user)
        is_chat = False

    if INFOPIC:
        if is_chat:
            try:
                pic = user.photo.big_file_id
                pfp = bot.get_file(pic).download(out=BytesIO())
                pfp.seek(0)
                message.reply_document(
                        document=pfp,
                        filename=f'{user.id}.jpg',
                        caption=text,
                        parse_mode=ParseMode.HTML,
                )
            except AttributeError:  # AttributeError means no chat pic so just send text
                message.reply_text(
                        text,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                )
        else:
            try:
                profile = bot.get_user_profile_photos(user.id).photos[0][-1]
                _file = bot.get_file(profile["file_id"])

                _file = _file.download(out=BytesIO())
                _file.seek(0)

                message.reply_document(
                        document=_file,
                        caption=(text),
                        parse_mode=ParseMode.HTML,
                )

            # Incase user don't have profile pic, send normal text
            except IndexError:
                message.reply_text(
                        text, parse_mode=ParseMode.HTML, disable_web_page_preview=True
                )

    else:
        message.reply_text(
            text, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )

def get_chat_info(user):
    text = (
        f"<b>Chat Info:</b>\n"
        f"<b>Title:</b> {user.title}"
    )
    if user.username:
        text += f"\n<b>Username:</b> @{html.escape(user.username)}"
    text += f"\n<b>Chat ID:</b> <code>{user.id}</code>"
    text += f"\n<b>Chat Type:</b> {user.type.capitalize()}"
    text += "\n" + chat_count(user.id)

    return text

def get_user_info(chat: Chat, user: User) -> str:
    bot = dispatcher.bot
    text = (
        f"<b>General:</b>\n"
        f"ID: <code>{user.id}</code>\n"
        f"First Name: {html.escape(user.first_name)}"
    )
    if user.last_name:
        text += f"\nLast Name: {html.escape(user.last_name)}"
    if user.username:
        text += f"\nUsername: @{html.escape(user.username)}"
    text += f"\nPermanent user link: {mention_html(user.id, 'link')}"
    num_chats = sql.get_user_num_chats(user.id)
    text += f"\n<b>Chat count</b>: <code>{num_chats}</code>"
    if user.id == OWNER_ID:
        text += "The disaster level of this person is God."
    elif user.id in DEV_USERS:
        text += "The disaster level of this person is Developer."
    elif user.id in DRAGONS:
        text += "The disaster level of this person is a part of Royal Union"
    elif user.id in DEMONS:
        text += "The disaster level of this person is a supporter of Royal Union"
    elif user.id in TIGERS:
        text += "The disaster level of this person is a tiger."
    elif user.id in WOLVES:
        text += "The disaster level of this person is a wolf."
    text += "\n"

    for mod in USER_INFO:
        if mod.__mod_name__ == "Users":
            continue
        try:
            mod_info = mod.__user_info__(user.id)
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id)
        if mod_info:
            text += "\n" + mod_info

    return text

__help__ = """
-> `/id`
get the current group id. If used by replying to a message, gets that user's id.
-> `/gifid`
reply to a gif to me to tell you its file ID.
-> `/info`
get information about a user.
-> `/markdownhelp`
quick summary of how markdown works in telegram - can only be called in private chats.
"""

ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True)
GIFID_HANDLER = DisableAbleCommandHandler("gifid", gifid)
PING_HANDLER = DisableAbleCommandHandler("ping", ping)
INFO_HANDLER = DisableAbleCommandHandler("info", info, pass_args=True)
ECHO_HANDLER = DisableAbleCommandHandler("echo", echo, filters=Filters.group)
MD_HELP_HANDLER = CommandHandler(
    "markdownhelp",
    markdown_help,
    filters=Filters.private)

dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(GIFID_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(PING_HANDLER)

__mod_name__ = "Misc"
__command_list__ = ["id", "info", "echo"]
__handlers__ = [
    ID_HANDLER,
    GIFID_HANDLER,
    INFO_HANDLER,
    ECHO_HANDLER,
    MD_HELP_HANDLER,
]
