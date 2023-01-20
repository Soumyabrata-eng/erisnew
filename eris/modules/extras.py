import os, requests, json, wikipedia, datetime, random
from eris.events import register
from eris.modules.disable import DisableAbleCommandHandler
from eris import telethn as tbot
from eris import pbot as tomori
from telegram import Update
from typing import List
from random import randint , randrange
from telegram import ParseMode, InputMediaPhoto, Update, TelegramError, ChatAction
from telegram.ext import CommandHandler, run_async, CallbackContext
from eris import dispatcher, TIME_API_KEY, CASH_API_KEY, WEATHER_API
from pytz import country_names as cname
from pyrogram import filters
from PIL import Image
from telegraph import Telegraph, exceptions, upload_file
from eris import TEMP_DOWNLOAD_DIRECTORY

telegraph = Telegraph()
r = telegraph.create_account(short_name="eris")
auth_url = r["auth_url"]


@register(pattern="^/tg(m|t) ?(.*)")
async def _(event):
    from datetime import datetime
    
    if event.fwd_from:
        return
    optional_title = event.pattern_match.group(2)
    if event.reply_to_msg_id:
        start = datetime.now()
        r_message = await event.get_reply_message()
        input_str = event.pattern_match.group(1)
        if input_str == "m":
            downloaded_file_name = await tbot.download_media(
                r_message, TEMP_DOWNLOAD_DIRECTORY
            )
            end = datetime.now()
            ms = (end - start).seconds
            h = await event.reply(
                "Downloaded to {} in {} seconds.".format(downloaded_file_name, ms)
            )
            if downloaded_file_name.endswith((".webp")):
                resize_image(downloaded_file_name)
            try:
                start = datetime.now()
                media_urls = upload_file(downloaded_file_name)
            except exceptions.TelegraphException as exc:
                await h.edit("ERROR: " + str(exc))
                os.remove(downloaded_file_name)
            else:
                end = datetime.now()
                (end - start).seconds
                os.remove(downloaded_file_name)
                await h.edit(
                    "Uploaded to https://te.legra.ph{})".format(media_urls[0]),
                    link_preview=True,
                )
        elif input_str == "t":
            user_object = await tbot.get_entity(r_message.sender_id)
            title_of_page = user_object.first_name  # + " " + user_object.last_name
            if optional_title:
                title_of_page = optional_title
            page_content = r_message.message
            if r_message.media:
                if page_content != "":
                    title_of_page = page_content
                downloaded_file_name = await tbot.download_media(
                    r_message, TEMP_DOWNLOAD_DIRECTORY
                )
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"
                os.remove(downloaded_file_name)
            page_content = page_content.replace("\n", "<br>")
            response = telegraph.create_page(title_of_page, html_content=page_content)
            end = datetime.now()
            ms = (end - start).seconds
            await event.reply(
                "Pasted to https://telegra.ph/{} in {} seconds.".format(
                    response["path"], ms
                ),
                link_preview=True,
            )
    else:
        await event.reply("Reply to a message to get a permanent telegra.ph link.")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")

def weather(update, context):
    args = context.args
    if len(args) == 0:
        reply = "Write a location to check the weather."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found") or (
                err.message == "Message can't be deleted"
            ):
                return

        return

    CITY = " ".join(args)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API}"
    request = requests.get(url)
    result = json.loads(request.text)
    if request.status_code != 200:
        reply = "Location not valid."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found") or (
                err.message == "Message can't be deleted"
            ):
                return
        return

    try:
        cityname = result["name"]
        curtemp = result["main"]["temp"]
        feels_like = result["main"]["feels_like"]
        humidity = result["main"]["humidity"]
        wind = result["wind"]["speed"]
        weath = result["weather"][0]
        condmain = weath["main"]
        conddet = weath["description"]
        country_name = cname[f"{result['sys']['country']}"]
        kmph = str(wind * 3.6).split(".")
    except KeyError:
        update.effective_message.reply_text("Invalid Location!")
        return

    def celsius(c):
        k = 273.15
        c = k if (c > (k - 1)) and (c < k) else c
        temp = str(round((c - k)))
        return temp

    def fahr(c):
        c1 = 9 / 5
        c2 = 459.67
        tF = c * c1 - c2
        if tF < 0 and tF > -1:
            tF = 0
        temp = str(round(tF))
        return temp

    reply = f"*Current weather for {cityname}, {country_name} is*:\n\n*Temperature:* `{celsius(curtemp)}°C ({fahr(curtemp)}ºF), feels like {celsius(feels_like)}°C ({fahr(feels_like)}ºF) \n`*Condition:* `{condmain}, {conddet}` \n*Humidity:* `{humidity}%`\n*Wind:* `{kmph[0]} km/h`\n"
    del_msg = update.effective_message.reply_text(
        "{}".format(reply),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )
    time.sleep(30)
    try:
        del_msg.delete()
        update.effective_message.delete()
    except BadRequest as err:
        if (err.message == "Message to delete not found") or (
            err.message == "Message can't be deleted"
        ):
            return

def nsfw(update,context):
    seko=['blowjob','trap','neko','waifu']
    randex = seko[randrange(len(seko))]
    chat_id = update.effective_chat.id
    msg = update.effective_message
    url = "https://api.waifu.pics/nsfw/" + randex
    result = requests.get(url).json()
    img = result['url']
    msg.reply_photo(img)

def webss(update: Update, context: CallbackContext):
    args = context.args
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    url = " ".join(args)
    chat_id = update.effective_chat.id
    bot = context.bot
    try:
        msg.reply_text(url)
        ss_url = "https://api.screenshotlayer.com/api/capture?access_key=ed5c9f4f66729019d4a0ec6bdcabd5bd&viewport=2220x1080&format=png&url={}"
        response = requests.get(ss_url.format(url))
        image = response.content
        bot.send_photo(chat_id=chat_id, photo=image)

    except Exception as e:
         msg.reply_text("API is not responding or query is wrong.")
         return

def ud(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text[len('/ud '):]
    results = requests.get(
        f'http://api.urbandictionary.com/v0/define?term={text}').json()
    try:
        reply_text = f'*{text}*\n\n{results["list"][0]["definition"]}\n\n_{results["list"][0]["example"]}_\n\n_{results["list"][0]["author"]}_'
    except Exception:
        reply_text = "No results found."
    message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)

def wall(update: Update, context: CallbackContext):
    args = context.args
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    query = " ".join(args)
    chat_id = update.effective_chat.id
    bot = context.bot
    url = requests.get(f"https://api.safone.me/wall?query={query}").json()["results"]
    ran = random.randint(0, 5)
    wallpaper=url[ran]["imageUrl"]
    bot.send_photo(
          chat_id,
          photo=wallpaper,
          caption='Made by @ErisRobot_bot',
          reply_to_message_id=msg_id, 
          timeout=60)

def wiki(update: Update, context: CallbackContext):
    args = context.args
    reply = " ".join(args)
    summary = '{} {}'
    update.message.reply_text(summary.format(wikipedia.summary(reply,sentences=10),  wikipedia.page(reply).url))

def cconvert(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(" ")
    if len(args) == 4:
        try:
            orig_cur_amount = float(args[1])
        except ValueError:
            update.effective_message.reply_text("Invalid Amount Of Currency")
            return
        orig_cur = args[2].upper()
        new_cur = args[3].upper()
        request_url = (
            f"https://www.alphavantage.co/query"
            f"?function=CURRENCY_EXCHANGE_RATE"
            f"&from_currency={orig_cur}"
            f"&to_currency={new_cur}"
            f"&apikey={CASH_API_KEY}"
        )
        response = requests.get(request_url).json()
        try:
            current_rate = float(
                response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
            )
        except KeyError:
            update.effective_message.reply_text("Currency Not Supported.")
            return
        new_cur_amount = round(orig_cur_amount * current_rate, 5)
        update.effective_message.reply_text(
            f"{orig_cur_amount} {orig_cur} = {new_cur_amount} {new_cur}"
        )

    elif len(args) == 1:
        update.effective_message.reply_text(__help__, parse_mode=ParseMode.MARKDOWN)

    else:
        update.effective_message.reply_text(f"*Invalid Args!!:* Required 3 But Passed {len(args) -1}",parse_mode=ParseMode.MARKDOWN) 

def generate_time(to_find: str, findtype: List[str]) -> str:
    data = requests.get(
        f"https://api.timezonedb.com/v2.1/list-time-zone"
        f"?key={TIME_API_KEY}"
        f"&format=json"
        f"&fields=countryCode,countryName,zoneName,gmtOffset,timestamp,dst"
    ).json()

    for zone in data["zones"]:
        for eachtype in findtype:
            if to_find in zone[eachtype].lower():
                country_name = zone["countryName"]
                country_zone = zone["zoneName"]
                country_code = zone["countryCode"]

                if zone["dst"] == 1:
                    daylight_saving = "Yes"
                else:
                    daylight_saving = "No"

                date_fmt = r"%d-%m-%Y"
                time_fmt = r"%H:%M:%S"
                day_fmt = r"%A"
                gmt_offset = zone["gmtOffset"]
                timestamp = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=gmt_offset)
                current_date = timestamp.strftime(date_fmt)
                current_time = timestamp.strftime(time_fmt)
                current_day = timestamp.strftime(day_fmt)

                break

    try:
        result = (
            f"<b>Country:</b> <code>{country_name}</code>\n"
            f"<b>Zone Name:</b> <code>{country_zone}</code>\n"
            f"<b>Country Code:</b> <code>{country_code}</code>\n"
            f"<b>Daylight saving:</b> <code>{daylight_saving}</code>\n"
            f"<b>Day:</b> <code>{current_day}</code>\n"
            f"<b>Current Time:</b> <code>{current_time}</code>\n"
            f"<b>Current Date:</b> <code>{current_date}</code>\n"
            '<b>Timezones:</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">List here</a>'
        )
    except:
        result = None

    return result


def gettime(update: Update, context: CallbackContext):
    message = update.effective_message

    try:
        query = message.text.strip().split(" ", 1)[1]
    except:
        message.reply_text("Provide a country name/abbreviation/timezone to find.")
        return
    send_message = message.reply_text(
        f"Finding timezone info for <b>{query}</b>", parse_mode=ParseMode.HTML
    )

    query_timezone = query.lower()
    if len(query_timezone) == 2:
        result = generate_time(query_timezone, ["countryCode"])
    else:
        result = generate_time(query_timezone, ["zoneName", "countryName"])

    if not result:
        send_message.edit_text(
            f"Timezone info not available for <b>{query}</b>\n"
            '<b>All Timezones:</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">List here</a>',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    send_message.edit_text(
        result, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )
    
UD_HANDLER = DisableAbleCommandHandler("ud", ud, pass_args=True)
WALL_HANDLER = DisableAbleCommandHandler("wall", wall, pass_args=True)
CONVERTER_HANDLER = DisableAbleCommandHandler('cash', cconvert, pass_args=True)
NSFW_HANDLER = DisableAbleCommandHandler("nsfw", nsfw, pass_args=True)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki, pass_args=True)
WEBSS_HANDLER = DisableAbleCommandHandler("webss", webss, pass_args=True)
WEATHER_HANDLER =  DisableAbleCommandHandler("weather", weather, pass_args=True)
TIME_HANDLER = DisableAbleCommandHandler("time",gettime, pass_args=True)

dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(WALL_HANDLER)
dispatcher.add_handler(WEATHER_HANDLER)
dispatcher.add_handler(NSFW_HANDLER)
dispatcher.add_handler(CONVERTER_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(WEBSS_HANDLER)
dispatcher.add_handler(TIME_HANDLER)

__handlers__ = [
    CONVERTER_HANDLER,
    WALL_HANDLER,
    NSFW_HANDLER,
    WIKI_HANDLER,
    TIME_HANDLER,
    WEBSS_HANDLER,
    WEATHER_HANDLER,
    UD_HANDLER ]

__mod_name__ = "Extras"

__help__ = """
──「 *Urban Dictionary:* 」──
-> `/ud` <word>: Type the word or expression you want to search use.

──「 *NSFW:* 」──
-> `/nsfw` <word>: Search nekos images around

──「 *Webss:* 」──
-> `/webss` <website>: website should be http://<website-name>.com

──「 *Timezone:* 」──
-> `/time` <zone>: Get the time zone of a country

──「 *Telegraph:* 」──
-> `/tgm or /tgt` <file>: Get the telegra.ph link

──「 *Currency Converter:* 」──
Example syntax: `/cash 1 USD INR`
-> `/cash`
currency converter

──「 *Wallpapers:* 」──
-> `/wall` <query> : get a wallpaper from the bot
"""
