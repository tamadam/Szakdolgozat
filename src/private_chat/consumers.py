from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


import json

from .models import *
from account.utils import EncodeAccountObject

from .utils import *
from django.utils import timezone

from core.constants import *


from .exceptions import ClientError, handle_client_error

from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize


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
		try:
			if self.room_id != None:
				await self.leave_room(self.room_id)
		except Exception as e:
			print('Disconnect')
			pass



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
				message = content['message']
				if len(message.lstrip()) == 0: # ha !=0val nezzuk es akkor kuldjuk a messaget akkor nem dob mindig errort ha empty message van
					raise ClientError(422, 'Empty message not allowed')
				await self.send_chat_message_to_room(room_id, message)
			elif command == 'join':
				await self.join_room(room_id)
			elif command == 'leave':
				await self.leave_room(room_id)
			elif command == 'get_private_chat_room_messages':
				# szoba, uzenetek payload és küldés
				room = await get_private_chat_room(room_id, user)

				page_number = content['page_number']

				info_packet = await get_private_chat_room_messages(room, page_number)
				if info_packet != None:
					info_packet = json.loads(info_packet) # decode json
					await self.send_previous_messages_payload(info_packet['messages'], info_packet['load_page_number'])
				else:
					raise ClientError('ERROR', 'Error when loading chat room messages')
			elif command == 'get_info_about_user':
				room = await get_private_chat_room(room_id, user)
				info_packet = await get_users(room, user)
				#info_packet = get_user_information(room, user1, user2)
				print('visszater')
				if info_packet != None:
					info_packet = json.loads(info_packet)
					await self.send_info_about_user_payload(info_packet['user_information'])
				else:
					raise ClientError('ERROR', 'Error when send info about user')
		except ClientError as e:
			error = await handle_client_error(e)
			print('# ' + str(error))
			await self.send_json(error)



	async def send_chat_message_to_room(self, room_id, message):
		"""
		receive_json függvény hívja meg, mikor valaki üzenetet küld a chatszobába
		Ez a függvény kezdi meg azt a folyamatot, hogy a payloadot az egész groupnak elküldje, ilyenkor 2 usernek
		"""
		user = self.scope['user']
		print('PrCRConsumer: send_chat_message_to_room from user: ' + user.username)
		if self.room_id != None: # valaki benne van egy szobában
			if str(room_id) != str(self.room_id): #
				raise ClientError('ROOM_ACCESS_DENIED', 'Room access denied')
		else:
			raise ClientError('ROOM_ACCESS_DENIED', 'Room access denied')

		# itt a felhasználó a megfelelő szobában van már
		room = await get_private_chat_room(room_id, user)

		try:
			profile_image = user.profile_image.url
		except Exception as e:
			profile_image = STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET

		await save_private_chat_room_message(user, room, message)



		await self.channel_layer.group_send(
			room.group_name,
			{
				'type': 'chat.message', # chat_message
				'user_id': user.id,
				'username': user.username,
				'profile_image': profile_image,
				'message': message
			}
		)

	async def chat_message(self, event):
		"""
		Mikor valaki üzenetet küld a chatbe
		"""

		#üzenet küldés a kliensnek (send a payload back to the template); backend stuff
		print('PrCRConsumer: chat_message from user: ' + str(event['username']))

		sending_time = create_sending_time(timezone.now())

		await self.send_json({
				'message_type': MESSAGE_TYPE_MESSAGE,
				'user_id': event['user_id'],
				'username': event['username'],
				'profile_image': event['profile_image'],
				'message': event['message'],
				'sending_time': sending_time,
			})


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

		# tároljuk hogy a szobában vagyunk
		self.room_id = room_id

		# csoporthoz hozzáadás, hogy a csoport üzeneteket megkapják
		await self.channel_layer.group_add(
			room.group_name,
			self.channel_name
			)


		await self.send_json({
				'join': str(room_id),
				'username': user.username,
			})

		if user.is_authenticated:
			await self.channel_layer.group_send(
				room.group_name,
				{
					'type': 'join.chat',
					'room_id': room_id,
					'user_id': user.id,
					'username': user.username,
				}
				)


	async def leave_room(self, room_id):
		"""
		Mikor valaki leave parancsot küld, meghívódik
		"""
		print('PrCRConsumer: leave_room')
		user = self.scope['user']
		try:
			room = await get_private_chat_room(room_id, user)
		except ClientError as e:
			error = await handle_client_error(exception)
			print('# ' + str(error))
			await self.send_json(error)

		await self.channel_layer.group_send(
			room.group_name,
			{
				'type': 'leave.chat',
				'room_id': room_id,
				'user_id': user.id,
				'username': user.username,
			}
		)

		self.room_id = None

		# felhasználó törlése a csoportból, hogy ne kapja meg továbbra is az üzeneteket
		await self.channel_layer.group_discard(
			room.group_name,
			self.channel_name
			)

		await self.send_json({
				'leave': str(room.id)
			})


	async def send_previous_messages_payload(self, messages, load_page_number):
		"""
		Elküldi a viewnak a következő betöltött üzeneteket
		"""

		print('PrCRConsumer: send_loaded_messages_payload')
		# nem akarjuk szétküldeni a csoportnak ezt az üzenetet, ez csak a kliens szemszögéből számít
		# az adott kliens kéri le az üzeneteket, nem akarjuk, hogy a többi felhasználó is megkapja
		await self.send_json({
				'message_packet': 'message_packet', # ez az identifier, hogy az onmessage fgv tudja kezelni; a keyword a lenyeg a value csak hogy legyen
				'messages': messages,
				'load_page_number': load_page_number,
			})	


	async def send_info_about_user_payload(self, user_information):
		"""
		Ezzel a függvénnyel küldünk vissza a viewhoz felhasználói információt
		"""
		print('PrCRConsumer: send_info_about_user_payload')

		await self.send_json({
				'user_information': user_information,
			})


	async def join_chat(self, event):
		if event['username']:
			await self.send_json({
					'message_type': MESSAGE_TYPE_JOIN,
					'room_id': event['room_id'],
					'user_id': event['user_id'],
					'username': event['username'],
				})


	async def leave_chat(self, event):
		if event['username']:
			await self.send_json({
					'message_type': MESSAGE_TYPE_LEAVE,
					'room_id': event['room_id'],
					'user_id': event['user_id'],
					'username': event['username'],
				})

@database_sync_to_async
def get_private_chat_room(room_id, user):
	"""
	Privát chatszobát szerez a felhasználónak
	"""
	try:
		room = PrivateChatRoom.objects.get(id=room_id)
	except PrivateChatRoom.DoesNotExist:
		raise ClientError('ERROR', 'Invalid error')

	if user != room.user1 and user != room.user2:
		raise ClientError('ERROR', 'Permission error')


	return room


# üzenetek mentése az adatbázisba
@database_sync_to_async
def save_private_chat_room_message(user, room, message):
	return PrivateChatRoomMessage.objects.create(user=user, room=room, content=message)



@database_sync_to_async
def get_users(room, user):
	"""
	user1 = room.user1
	user2 = room.user2
	print(f'felhasznalok: {user1} és {user2}')
	return user1, user2
	"""
	other_user = room.user1
	curr_user = room.user2
	if other_user == user:
		other_user = room.user2
		curr_user = room.user1

	print(f'felhasznalok: {other_user} és {curr_user}')

	info_packet = {}

	s = EncodeAccountObject() # listát ad vissza

	info_packet['user_information'] = s.serialize([other_user])[0]
	return json.dumps(info_packet)


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


@database_sync_to_async
def get_private_chat_room_messages(room, page_number):
	"""
	Privát chatszoba üzeneteinek lekérdezése, egyszerre egy megadott érték szerint
	"""
	try:	
		p = Paginator(PrivateChatRoomMessage.objects.get_chat_messages_by_room(room), PRIVATE_CHAT_ROOM_MESSAGE_PAGE_SIZE)


		message = {}

		load_page_number = int(page_number)


		# elértük e az utolsó oldalt
		if load_page_number <= p.num_pages:
			load_page_number = load_page_number + 1
			
			s = EncodePrivateChatRoomMessage()

			message['messages'] = s.serialize(p.page(page_number).object_list)

		else:

			message['messages'] = 'None'
		message['load_page_number'] = load_page_number

		# python szótár konvertálása JSON objektummá és visszatérés az értékkel

		return json.dumps(message)
	except Exception as e:
		print('ERROR WHEN GETTING CHAT MESSAGES' + str(e))

	return None



# mehet majd a utilsba, ez ahhoz kell hogy lekerjuk a regebbi chat uzeneteket
class EncodePrivateChatRoomMessage(Serializer):
	def get_dump_object(self, obj):
		"""
		PrivateChatRoomMessage object szerializálása, mikor payload-ként küldjük a view-hoz
		JSON formátumra alakítjuk
		Függvény egy override
		"""

		# ez a try except azért kell, hogyha nincs valakinek profilképe, akkor a default helyen lévőt állítsa be hozzá
		try:
			profile_image = str(obj.user.profile_image.url)
		except Exception as e:
			profile_image = STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET

		message_obj = {
			'message_id'	: 	str(obj.id),
			'message_type'	:	MESSAGE_TYPE_MESSAGE,
			'message'		:	str(obj.content),
			'user_id'		:	str(obj.user.id),
			'username'		:	str(obj.user.username),
			#'profile_image'	:  	str(object.user.profile_image.url),
			'profile_image'	:	profile_image,
			'sending_time'	:	create_sending_time(obj.sending_time),
		}

		return message_obj
		