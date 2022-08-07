from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType

import json
from datetime import datetime

from core.constants import *

from private_chat.models import UnreadPrivateChatRoomMessages

from .models import Notification

class NotificationConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		"""
		Csatlakozáskor használjuk, a kezdeti fázisban mikor a szerver és a kliens websocket kapcsolatra vált
		"""
		print('NotificationConsumer: ' + str(self.scope['user']) + ' connected') 

		await self.accept()


	async def disconnect(self, code):
		"""
		Mikor bezáródik a websocket kapcsolat a szerver és kliens között
		"""
		print('NotificationConsumer: ' + str(self.scope['user']) + ' disconnected')



	async def receive_json(self, content, **kwargs):
		"""
		Dekódolt JSON üzenet, akkor hívódik meg, mikor valamilyen parancs érkezik a template-től
		Első argumentumban van benne
		"""
		command = content.get('command', None) 
		print('NotificationConsumer: receive_json called with command: ' + str(command))

		try:
			if command == 'get_unread_chat_notifications_count':
				try:
					payload = await get_unread_chat_notification_count(self.scope["user"])
					if payload != None:
						payload = json.loads(payload)
						await self.send_unread_chat_notification_count(payload['count'])
				except Exception as e:
					print("UNREAD CHAT MESSAGE COUNT EXCEPTION: " + str(e))
					pass
		except:
			pass

	async def send_unread_chat_notification_count(self, count):
		"""
		Send the number of unread "chat" notifications to the template
		"""
		await self.send_json(
			{
				"message_type": MESSAGE_TYPE_NOTIFICATIONS_COUNT,
				"num": count,
			},
		)

@database_sync_to_async
def get_unread_chat_notification_count(user):
    print('hey')
    payload = {}
    if user.is_authenticated:
        chatmessage_ct = ContentType.objects.get_for_model(UnreadPrivateChatRoomMessages)
        notifications = Notification.objects.filter(notified_user=user, content_type__in=[chatmessage_ct])

        unread_count = 0
        if notifications:
            unread_count = len(notifications.all())
        payload['count'] = unread_count
        return json.dumps(payload)
    else:
        #raise ClientError("AUTH_ERROR", "User must be authenticated to get notifications.")
        pass
    return None

