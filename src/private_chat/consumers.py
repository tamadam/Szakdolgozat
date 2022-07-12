from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize

import json

from .models import *
from account.utils import EncodeAccountObject

from .exceptions import ClientError, handle_client_error

class PrivateChatRoomConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		"""
		Csatlakozáskor használjuk, a kezdeti fázisban mikor a szerver és a kliens websocket kapcsolatra vált
		"""
		print('PrCRConsumer: ' + str(self.scope['user']) + ' connected') 
		await self.accept()

		self.room_id = None


	async def disconnect(self, code):
		"""
		Mikor bezáródik a websocket kapcsolat a szerver és kliens között
		"""
		print('PrCRConsumer: ' + str(self.scope['user']) + ' disconnected') 



	async def receive_json(self, content, **kwargs):
		"""
		Dekódolt JSON üzenet, meghívódik mikor egy üzenetkeret jön
		"""

		# https://www.w3schools.com/python/ref_dictionary_get.asp
		command = content.get('command', None) # payloadot kaptunk a templatettől
		room_id = content.get('room_id')
		user = self.scope['user']

		print('PrCRConsumer: receive_json called with command: ' + str(command))


		try:
			if command == 'send':
				pass
			elif command == 'join':
				await self.join_room(room_id)
			elif command == 'leave':
				pass
			elif command == 'get_private_chat_room_messages':
				pass
			elif command == 'get_info_about_user':
				room = await get_private_chat_room(room_id, user)
				user1, user2 = await get_users(room, user)
				info_packet = get_user_information(room, user1, user2)
				if info_packet != None:
					info_packet = json.loads(info_packet)
					await self.send_info_about_user_payload(info_packet['user_information'])
				else:
					raise ClientError('Error when send info about user')
		except ClientError as e:
			error = await handle_client_error(e)
			print('# ' + str(error))
			await self.send_json(error)



	async def send_chat_message_to_room(self, room_id, message):
		"""
		receive_json függvény hívja meg, mikor valaki üzenetet küld a chatszobába
		"""
		user = self.scope['user']
		print('PrCRConsumer: send_chat_message_to_room from user: ' + user.username)




	async def chat_message(self, event):
		"""
		Mikor valaki üzenetet küld a chatbe
		"""

		#üzenet küldés a kliensnek (send a payload back to the template); backend stuff
		print('PrCRConsumer: chat_message from user: ' + str(event['username']))



	async def join_room(self, room_id):
		"""
		Miután létrejött a websocket kapcsolat, küldünk egy payload-ot hogy a felhasználó csatlakozzon a szobához
		Mikor valaki join parancsot küld, akkor hívódik meg
		"""
		print('PrCRConsumer: join_room')
		user = self.scope['user']
		try:
			room = await get_private_chat_room(room_id, user)
		except ClientError as e:
			error = await handle_client_error(exception)
			print('# ' + str(error))
			await self.send_json(error)

		await self.send_json({
				'join': str(room_id),
				'username': user.username,
			})


	async def leave_room(self, room_id):
		"""
		Mikor valaki leave parancsot küld, meghívódik
		"""
		print('PrCRConsumer: leave_room')
		

	async def send_previous_messages_payload(self, messages, load_page_number):
		"""
		Elküldi a viewnak a következő betöltött üzeneteket
		"""

		print('PrCRConsumer: send_loaded_messages_payload')


	async def send_info_about_user_payload(self, user_information):
		"""
		Ezzel a függvénnyel küldünk vissza a viewhoz felhasználói információt
		"""
		print('PrCRConsumer: send_info_about_user_payload')

		await self.send_json({
				'user_information': user_information,
			})


	async def join_chat(self, event):
		pass


	async def leave_chat(self, event):
		pass


@database_sync_to_async
def get_private_chat_room(room_id, user):
	"""
	Privát chatszobát szerez a felhasználónak
	"""
	try:
		room = PrivateChatRoom.objects.get(id=room_id)
	except PrivateChatRoom.DoesNotExist:
		raise ClientError('Invalid error')

	if user != room.user1 and user != room.user2:
		raise ClientError('Permission error')


	return room


@database_sync_to_async
def get_users(room, user):
	user1 = room.user1
	user2 = room.user2
	print(f'felhasznalok: {user1} és {user2}')
	return user1, user2


def get_user_information(room, user1, user2):
	"""
	Felhasználó információ beszerzése a másik felhasználóról
	Visszatérési értéke: a felhasználóról az info vagy None
	"""


	try:
		info_packet = {}
		s = EncodeAccountObject() # listát ad vissza
		info_packet['user_information'] = s.serialize([user2])[0]
		return json.dumps(info_packet)

	except Exception as e:
		print('ERROR when getting user info')

	return None