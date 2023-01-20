from pytgcalls import StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from pytgcalls.exceptions import NoActiveGroupCall,NotInGroupCallError
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
import telethon.utils
from telethon.tl import functions
from telethon.tl import types
from telethon.utils import get_display_name
from telethon.tl.functions.users import GetFullUserRequest
from youtubesearchpython import VideosSearch
from eris import config 

from eris import call_py, telethn as aid, client as Client
from eris.helpers.yt_dlp import bash
from eris.helpers.queues import QUEUE, add_to_queue, get_queue, pop_an_item, active, clear_queue
from telethon import Button, events

from eris.events import register
from eris.helpers.thumbnail import gen_thumb
from eris.helpers.joiner import AssistantAdd
import functools

def is_admin(func):
    @functools.wraps(func)
    async def a_c(event):
        is_admin = False
        if not event.is_private:
            try:
                _s = await event.client.get_permissions(event.chat_id, event.sender_id)
                if _s.is_admin:
                    is_admin = True
            except:
                is_admin = False
        if is_admin:
            await func(event, _s)
        else:
            await event.reply("Only Admins can execute this command!")
    return a_c

erisplay = "https://te.legra.ph/file/d1aa5970e64feff1a8924.jpg"
owner = "5061699559" 

def vcmention(user):
    full_name = get_display_name(user)
    if not isinstance(user, types.User):
        return full_name
    return f"[{full_name}](tg://user?id={user.id})"


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        videoid = data["id"]
        return [songname, url, duration, thumbnail, videoid]
    except Exception as e:
        print(e)
        return 0


async def ytdl(format: str, link: str):
    stdout, stderr = await bash(f'yt-dlp -g -f "{format}" {link}')
    if stdout:
        return 1, stdout.split("\n")[0]
    return 0, stderr


async def skip_item(chat_id: int, x: int):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    try:
        songname = chat_queue[x][0]
        chat_queue.pop(x)
        return songname
    except Exception as e:
        print(e)
        return 0


async def skip_current_song(chat_id: int):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    if len(chat_queue) == 1:
        await call_py.leave_group_call(chat_id)
        clear_queue(chat_id)
        active.remove(chat_id)
        return 1
    songname = chat_queue[1][0]
    url = chat_queue[1][1]
    link = chat_queue[1][2]
    type = chat_queue[1][3]
    if type == "Audio":
        await call_py.change_stream(
            chat_id,
            AudioPiped(
                url,
            ),
        )
    pop_an_item(chat_id)
    return [songname, link, type]

btn =[
    [Button.url("Donate 🕊", url=f"https://buymeacoffee.com/htcworld")],
    [Button.inline("Close 🗑️", data="cls")]]


@register(pattern="^[/?!.]play ?(.*)")
@AssistantAdd
async def play(event):
    title = ' '.join(event.text[5:])
    replied = await event.get_reply_message()
    sender = await event.get_sender()
    chat = await event.get_chat()
    chat_id = event.chat_id
    from_user = vcmention(event.sender) 
    public = event.chat_id
    if (
        replied
        and not replied.audio
        and not replied.voice
        and not title
        or not replied
        and not title
    ):
        return await event.client.send_file(chat_id, Config.CMD_IMG, caption="Give me any query of song\n Example: `/play sorry`", buttons=btn)
    elif replied and not replied.audio and not replied.voice or not replied:
        botman = await event.reply("🔄 Processing Query... Please wait!")
        query = event.text.split(maxsplit=1)[1]
        search = ytsearch(query)
        if search == 0:
            await botman.edit("The desired song could not be found.")     
        else:
            songname = search[0]
            title = search[0]
            url = search[1]
            duration = search[2]
            thumbnail = search[3]
            videoid = search[4]
            userid = sender.id
            titlegc = chat.title
            thumb = await gen_thumb(videoid)
            format = "best[height<=?720][width<=?1280]"
            hm, ytlink = await ytdl(format, url)
            if hm == 0:
                await botman.edit(f"`{ytlink}`")
            elif chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                caption = f"⌛ Added to Queue at #{pos}\n\n💡 **Title:** [{songname}]({url})\n**⏰ Duration:** `{duration}`\n👥 **Requested By:** {from_user}"
                await botman.delete()
                await event.client.send_file(chat_id, thumb, caption=caption, buttons=btn)
            else:
                try:
                    await call_py.join_group_call(
                        chat_id,
                        AudioPiped(
                            ytlink,
                        ),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                    caption = f"📡 Started Streaming 💡\n\n💡 **Title:** [{songname}]({url})\n**⏰ Duration:** `{duration}`\n👥 **Requested By:** {from_user}"
                    await botman.delete()
                    await event.client.send_file(chat_id, thumb, caption=caption, buttons=btn)
                except Exception as ep:
                    clear_queue(chat_id)
                    await botman.edit(f"`{ep}`")

    else:
        botman = await edit_or_reply(event, "➕ Downloading File...")
        dl = await replied.download_media()
        link = f"https://t.me/c/{chat.id}/{event.reply_to_msg_id}"
        if replied.audio:
            songname = "Telegram Music Player"
        elif replied.voice:
            songname = "Voice Note"
        if chat_id in QUEUE:
            pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
            caption = f"⌛ Added to Queue at #{pos}\n**💡 Title:** [{songname}]({link})\n👥 **Requested By:** {from_user}"
            await event.client.send_file(chat_id, erisplay, caption=caption, buttons=btn)
            await botman.delete()
        else:
            try:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                caption = f"📡 Started Streaming 💡\n\n💡 **Title:** [{songname}]({link})\n👥 **Requested By:** {from_user}"
                await event.client.send_file(chat_id, erisplay, caption=caption, buttons=btn)
                await botman.delete()
            except Exception as ep:
                clear_queue(chat_id)
                await botman.edit(f"`{ep}`")


@register(pattern="^[/?!.]end ?(.*)")
@is_admin
async def vc_end(event, perm):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await event.reply("Streaming Ended")
        except Exception as e:
            await event.reply(f"ERROR: `{e}`")
    else:
        await event.reply("Not streaming now !")


@aid.on(events.NewMessage(pattern="^[?!/.]playlist"))
@is_admin
async def vc_playlist(event, perm):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await event.reply(
                f"PlayList: \n• [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",
                link_preview=False,
            )
        else:
            PLAYLIST = f"🎧 PLAYLIST:\n• [{chat_queue[0][0]}]({chat_queue[0][2]})** | `{chat_queue[0][3]}` \n\n**• Upcoming Streaming:**"
            l = len(chat_queue)
            for x in range(1, l):
                hm1 = chat_queue[x][0]
                hm2 = chat_queue[x][2]
                hm3 = chat_queue[x][3]
                PLAYLIST = PLAYLIST + "\n" + \
                    f"**#{x}** - [{hm1}]({hm2}) | `{hm3}`"
            await event.reply(PLAYLIST, link_preview=False)
    else:
        await event.reply("Not Streaming Now")



@aid.on(events.NewMessage(pattern="^[?!/.]leavevc"))
@is_admin
async def leavevc(event, perm):
    xnxx = await event.reply("Processing")
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    if from_user:
        try:
            await call_py.leave_group_call(chat_id)
        except (NotInGroupCallError, NoActiveGroupCall):
            pass
        await xnxx.edit("Left the voice chat `{}`".format(str(event.chat_id)))
    else:
        await xnxx.edit(f"Sorry {owner} is not on vc.")



@aid.on(events.NewMessage(pattern="^[?!/.]skip"))
@is_admin
async def vc_skip(event, perm):
    chat_id = event.chat_id
    if len(event.text.split()) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await event.reply("Nothing Is Streaming")
        elif op == 1:
            await event.reply("Empty Queue, leave voice chat", 10)
        else:
            await event.reply(
                f"⏭ Skipped\n**🎧 Now Playing** - [{op[0]}]({op[1]})",
                link_preview=False,
            )
    else:
        skip = event.text.split(maxsplit=1)[1]
        DELQUE = "**Removing Following Songs From Queue:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x != 0:
                    hm = await skip_item(chat_id, x)
                    if hm != 0:
                        DELQUE = DELQUE + "\n" + f"**#{x}** - {hm}"
            await event.reply(DELQUE)


@aid.on(events.NewMessage(pattern="^[?!/.]pause"))
@is_admin
async def vc_pause(event, perm):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await event.reply("Streaming Paused")
        except Exception as e:
            await event.reply(f"ERROR: `{e}`")
    else:
        await event.reply("Nothing Is Playing")



@aid.on(events.NewMessage(pattern="^[?!/.]resume"))
@is_admin
async def vc_resume(event, perm):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await event.reply("Streaming Started Back 🔙")
        except Exception as e:
            await event.reply(f"ERROR: `{e}`")
    else:
        await event.reply("Nothing Is Streaming")


@call_py.on_stream_end()
async def stream_end_handler(_, u: Update):
    chat_id = u.chat_id
    print(chat_id)
    await skip_current_song(chat_id)


@call_py.on_closed_voice_chat()
async def closedvc(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
    if chat_id in active:
        active.remove(chat_id)


@call_py.on_left()
async def leftvc(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
    if chat_id in active:
        active.remove(chat_id)


@call_py.on_kicked()
async def kickedvc(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
    if chat_id in active:
        active.remove(chat_id)

__mod_name__ = "Music"

__help__ = """
-> `/play` text
plays the track

-> `/playlist` text
displays entire playlist of tracks in queue.

-> `/skips` text
skips the track

-> `/resume` text
resume the track

-> `/pause` text
pause the track

-> `/reload` text
reloads admin list.

-> `/end` text
ends the vc
"""