from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from public_chat.consumers import PublicChatRoomConsumer
from private_chat.consumers import PrivateChatRoomConsumer

"""
###   Django channels kapcsolódó dokumentáció: https://channels.readthedocs.io/en/latest/topics/routing.html#   ###

1. ProtocolTypeRouter : ennek segítségével definiálhatjuk milyen típusú ASGI appot készítünk [websocket típus]

2. AllowedHostsOriginValidator : domainek halmaza, amelyek használhatják ezt a websocketet [ALLOWED_HOSTS]

3. AuthMiddlewareStack :
		request.user-el elérjük az adott usert a viewsban --> ugyanezt meg tudjuk csinálni a websocketes kódban is
		--> self.scope['user'] : hozzáférést biztosít a user objecthez a sessionben a channel/websocket appon belül

4. URLRouter : 	a url-eket itt arra használjuk, hogy megmondjuk a django websocket toolnak,
				melyek azok a url-ek, amelyekhez websocketeket tudok csatlakoztatni
				(azoknak a url-eknek a listája, ahova a websocketet csatlakoztatjuk, amíg nincs consumer addig üres)

"""



application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack( 
			URLRouter([
				path('public_chat/<room_id>/', PublicChatRoomConsumer.as_asgi()),
				path('private_chat/<room_id>/', PrivateChatRoomConsumer.as_asgi()),
				]) 
			)
		),
	})