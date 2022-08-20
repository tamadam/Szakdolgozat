from datetime import datetime

#--PUBLIKUS CHAT SZOBA--#
PUBLIC_CHAT_ROOM_ID = 1 # fixen 1 db publikus chat szoba ID-ja


#--ÜZENETEK TÍPUSA--#
MESSAGE_TYPE_MESSAGE = 0 # normál üzenet
MESSAGE_TYPE_JOIN = 3 # felhasználó szobába belépését jelző üzenet 
MESSAGE_TYPE_LEAVE = 4 # felhasználó szobából kilépését jelző üzenet
MESSAGE_TYPE_ONLINE_USERS = 5 # a szobához csatlakozott felhasználók számát és nevét jelző üzenet
MESSAGE_TYPE_PRIVATE_NOTIFICATIONS_COUNT = 20
MESSAGE_TYPE_PUBLIC_NOTIFICATIONS_COUNT = 21
MESSAGE_TYPE_TEAM_NOTIFICATIONS_COUNT = 22

#--ÜZENETEK BETÖLTÉSE--#
PUBLIC_CHAT_ROOM_MESSAGE_PAGE_SIZE = 10 # oldalanként betöltött üzenetek száma a publikus chat szobában
PRIVATE_CHAT_ROOM_MESSAGE_PAGE_SIZE = 10 # oldalanként betöltött üzenetek száma a privát chat szobában
TEAM_ROOM_MESSAGE_PAGE_SIZE = 10 # oldalanként betöltött üzenetek száma a csapat chat szobában


#--ALAPÉRTELMEZETT PROFILKÉP HELYE--#
STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET = '/static/images/blank_profile_image.png'


#--ALAPÉRTELMEZETT XP ÉS ARANY NÖVEKEDÉS AZ EGYES JÁTÉKOK UTÁN--#
DEFAULT_XP_INCREASE_EASY_GAME = 30
DEFAULT_XP_INCREASE_MEDIUM_GAME = 80
DEFAULT_XP_INCREASE_HARD_GAME = 120

DEFAULT_GOLD_INCREASE_EASY_GAME = 10
DEFAULT_GOLD_INCREASE_MEDIUM_GAME = 40
DEFAULT_GOLD_INCREASE_HARD_GAME = 60


#--ALAPÉRTELMEZETT ÉRTÉK NÖVEKEDÉS A KÖVETKEZŐ SZINTHEZ--#
DEFAULT_NEXT_LEVEL_XP_INCREASE = 100
DEFAULT_ATTRIBUTE_INCREASE_PERCENTAGE = 1.08




SUCCESS_MESSAGE_ON_FINDING_PRIVATE_CHAT = 'Got your private chat'


DEFAULT_SENDING_TIME = datetime.strptime('Jan 1 1970  1:00AM', '%b %d %Y %I:%M%p')


DEFAULT_ATTRIBUTE_INCREASE_VALUE = 4