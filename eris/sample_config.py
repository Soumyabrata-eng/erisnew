import json
import os

def get_user_list(config, key):
    with open("{}/eris/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]

class Config(object):
    LOGGER = True
    API_ID = 6435225
    
    ## optional for music bot
    STRING_SESSION = "telethon string session"
    
    API_HASH = ""
    CASH_API_KEY = ""  # Get this value for currency converter from https://www.alphavantage.co/support/#api-key
    DATABASE_URL = ""  # A SQL database url from elephantsql.com
    EVENT_LOGS = ()  # Event logs channel to note down important bot level events.
    SUPPORT_CHAT = "bloggerminds" 
    TOKEN = ""  # Get bot token from @BotFather on Telegram
    TIME_API_KEY = ""  # Get this value from https://timezonedb.com/api
    OWNER_ID = 5480870128  # User id of your telegram account (Must be integer)
    
    ## optional for music bot
    ASSISTANT_ID =         # Assistant id of music bot
    
    
    WEATHER_API = "" # Get this from https://openweathermap.org/api.php
    SPAMWATCH_API = None

    # Optional fields
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    DEMONS = get_user_list("elevated_users.json", "supports")
    TIGERS = get_user_list("elevated_users.json", "tigers")
    WOLVES = get_user_list("elevated_users.json", "whitelists")
    BL_CHATS = []  # List of groups that you want blacklisted

    ALLOW_CHATS = True
    ALLOW_EXCL = True
    DEL_CMDS = True
    INFOPIC = True
    LOAD = []
    
    ## Make NO_LOAD = [] for music bot
    NO_LOAD = ["musictools","userbotjoin","activevoice"]
    
    STRICT_GBAN = True
    TEMP_DOWNLOAD_DIRECTORY = "./cache"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
