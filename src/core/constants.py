from datetime import datetime

#--PUBLIKUS CHAT SZOBA--#
PUBLIC_CHAT_ROOM_ID = 1 # fixen 1 db publikus chat szoba ID-ja


#--ÜZENETEK TÍPUSA--#
MESSAGE_TYPE_MESSAGE = 0 # normál üzenet
MESSAGE_TYPE_JOIN = 3 # felhasználó szobába belépését jelző üzenet 
MESSAGE_TYPE_LEAVE = 4 # felhasználó szobából kilépését jelző üzenet
MESSAGE_TYPE_ONLINE_USERS = 5 # a szobához csatlakozott felhasználók számát és nevét jelző üzenet
MESSAGE_TYPE_NOTIFICATIONS_COUNT = 20

#--ÜZENETEK BETÖLTÉSE--#
PUBLIC_CHAT_ROOM_MESSAGE_PAGE_SIZE = 10 # oldalanként betöltött üzenetek száma a publikus chat szobában
PRIVATE_CHAT_ROOM_MESSAGE_PAGE_SIZE = 10 # oldalanként betöltött üzenetek száma a privát chat szobában
TEAM_ROOM_MESSAGE_PAGE_SIZE = 10 # oldalanként betöltött üzenetek száma a csapat chat szobában


#--ALAPÉRTELMEZETT PROFILKÉP HELYE--#
STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET = '/static/images/blank_profile_image.png'





SUCCESS_MESSAGE_ON_FINDING_PRIVATE_CHAT = 'Got your private chat'


DEFAULT_SENDING_TIME = datetime.strptime('Jan 1 1970  1:00AM', '%b %d %Y %I:%M%p')


DEFAULT_ATTRIBUTE_INCREASE_VALUE = 4