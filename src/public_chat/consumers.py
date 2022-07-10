from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.conf import settings # import get_user_model-el hasonlo

from .exceptions import ClientError, get_chat_room, handle_client_error
from .constants import *

from .models import PublicChatRoom, PublicChatRoomMessage



# küldési időhöz
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils import timezone
from datetime import datetime, date

# chat üzenetek betöltése (pagination)
from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize


USER = settings.AUTH_USER_MODEL

# Docs : https://github.com/django/channels/blob/main/channels/generic/websocket.py


class PublicChatRoomConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		"""
		Csatlakozáskor használjuk, a kezdeti fázisban mikor a szerver és a kliens websocket kapcsolatra vált
		"""
		print('PCRConsumer: ' + str(self.scope['user']) + ' connected') 
		await self.accept()

		self.room_id = None


	async def disconnect(self, code):
		"""
		Mikor bezáródik a websocket kapcsolat a szerver és kliens között
		"""
		print('PCRConsumer: ' + str(self.scope['user']) + ' disconnected') 
		
		try:
			if self.room_id != None:
				await self.leave_room(self.room_id)
		except Exception as e:
			print('Something went wrong when leaving the room')
			pass



	async def receive_json(self, content, **kwargs):
		"""
		Dekódolt JSON üzenet, meghívódik mikor egy üzenetkeret jön
		"""

		# https://www.w3schools.com/python/ref_dictionary_get.asp
		command = content.get('command', None) # payloadot kaptunk a templatettől
		room_id = content['room_id']

		print('PCRConsumer: receive_json called with command: ' + str(command))


		#message = content['message'] csak akkor lesz message ha send van

		try:
			if command == 'send':
				message = content['message']
				if len(message.lstrip()) == 0:
					raise ClientError(422, 'Empty message not allowed')
				await self.send_chat_message_to_room(room_id, message)
			elif command == 'join':
				await self.join_room(room_id) #ez az a resz ahol room_id az room
			elif command == 'leave':
				await self.leave_room(room_id)
			elif command == 'get_public_chat_room_messages':
				page_number = content['page_number']

				#room = get_chat_room(room_id)

				messages_payload = await get_public_chat_room_messages(room_id, page_number) 

				if messages_payload != None:
					# JSON formátum átalakítása python szótárrá

					messages_payload = json.loads(messages_payload)

					await self.load_messages_payload(messages_payload['messages'], messages_payload['load_page_number'])
				else:
					raise ClientError(204, 'Something went wrong when getting PublicChatRoom messages')
		except ClientError as exception: # ha valamilyen hiba van, kihagyjuk a send_chat_message-t, hogy csak az adott személy kapja meg a hibaüzenetet
			error = await handle_client_error(exception)
			print('# ' + str(error))
			await self.send_json(error)



	async def send_chat_message_to_room(self, room_id, message):
		"""
		receive_json függvény hívja meg, mikor valaki üzenetet küld a chatszobába
		"""
		user = self.scope['user']
		print('PCRConsumer: send_chat_message_to_room from user: ' + user.username)


		if self.room_id != None:
			if str(room_id) != str(self.room_id):
				raise ClientError('Room access denied', 'Room access denied')
			if not user.is_authenticated:
				raise ClientError('Room access denied', 'Room access denied')
		else:
			raise ClientError('Room access denied', 'Room access denied')


		room = await get_chat_room(room_id)

		# üzenet mentése az adatbázisba
		await save_public_chat_room_message(user, room, message)

		await self.channel_layer.group_send(
			room.group_name,
			{
				'type': 'chat.message', # chat_message
				'user_id': self.scope['user'].id,
				'username': self.scope['user'].username,
				'profile_image': self.scope['user'].profile_image.url,
				'message': message
			}
		)


	async def chat_message(self, event):
		"""
		Mikor valaki üzenetet küld a chatbe
		"""

		#üzenet küldés a kliensnek (send a payload back to the template); backend stuff
		print('PCRConsumer: chat_message from user: ' + str(event['username']))


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
		print('PCRConsumer: join_room')


		try:
			room = await get_chat_room(room_id)
		except ClientError as exception:
			error = await handle_client_error(exception)
			print('# ' + str(error))
			await self.send_json(error)





		user = self.scope['user']
		if user.is_authenticated:
			print(f'PCRConsumer: add user {user.username} to online users in group {room.group_name} ') #ezert kellhetett a property a modellben
			await add_user(room, user)

		self.room_id = room.id

		# hogy megkapják mások is az üzenetet, hozzá kell adni őket a grouphoz a consumeren belül
		await self.channel_layer.group_add(
			room.group_name,
			self.channel_name
			)	

		# payloadot küldünk hogy csatlakoztunk a szobaba (js.ben: data.join)
		await self.send_json({
			'join': str(room.id),
			'username': user.username,
			})


		online_users = await get_room_users(room_id)
		await self.channel_layer.group_send(
				room.group_name,
				{
					'type': 'number.of.online.users',
					'online_users': online_users,
				}
			)


	async def leave_room(self, room_id):
		"""
		Mikor valaki leave parancsot küld, meghívódik
		"""
		print('PCRConsumer: leave_room')
		try:
			room = await get_chat_room(room_id)
		except ClientError as exception:
			error = await handle_client_error(exception) # ha nincs kiszervezve a függvény: self.handle..
			print('# ' + str(error))
			await self.send_json(error)



		user = self.scope['user']
		if user.is_authenticated:
			print(f'PCRConsumer: remove user {user.username} from online users in group {room.group_name} ') #ezert kellhetett a property a modellben
			await remove_user(room, user)

		self.room_id = None

		await self.channel_layer.group_discard(
				room.group_name,
				self.channel_name
			)


		online_users = await get_room_users(room_id)

		await self.channel_layer.group_send(
				room.group_name,
				{
					'type': 'number.of.online.users',
					'online_users': online_users,
				}
			)


	async def load_messages_payload(self, messages, load_page_number):
		"""
		Elküldi a viewnak a következő betöltött üzeneteket
		"""

		print('PCRConsumer: load_messages_payload')
		await self.send_json({
				'messages_payload': 'sent_messages',
				'messages': messages,
				'load_page_number': load_page_number,
			})


	async def number_of_online_users(self, event):
		"""
		Elküldi a szobához jelenleg csatlakozott felhasználók számát	
		"""
		#print('number_of_online_users')
		await self.send_json({
				'message_type': MESSAGE_TYPE_NUMBER_OF_ONLINE_USERS,
				'num_of_online_users': event['online_users'],
			})



@database_sync_to_async
def get_room_users(room_id):
    users = PublicChatRoom.objects.get(id=room_id).users
    if users:
        return len(users.all())
    return 0



def format_older_messages_sending_time(sending_time):
	months = {
		1 	: 'Január',
		2 	: 'Február',
		3 	: 'Március',
		4 	: 'Április',
		5 	: 'Május',
		6 	: 'Június',
		7 	: 'Július',
		8 	: 'Augusztus',
		9 	: 'Szeptember',
		10 	: 'Október',
		11 	: 'November',
		12 	: 'December',
	}

	current_day = timezone.now()
	#print('sendingtime' ,sending_time)


	year_month_day = str(sending_time).split()[0]
	#print('YMD:', year_month_day)
	year = year_month_day.split('-')[0]
	#print('year', year)
	month = int(year_month_day.split('-')[1].lstrip('0')) # 2022-07-07 19:17:47.314147 --> ['2022', '07', '07'] --> 7
	#print('month', month)
	day = year_month_day.split('-')[2]
	#print('day', day)

	#month_number = int(str(sending_time).split()[0].split('-')[1].lstrip('0')) 

	month_name = list({v for k,v in months.items() if k==month})[0]
	
	message_age_in_days = int(str(current_day-sending_time)[0])

	if message_age_in_days > 7:
		return f'{year}. {month_name}. {day}'
	elif message_age_in_days <= 7:
		return f'{message_age_in_days} napja'
	else:
		return 'ismeretlen küldési idő'



def format_today_messages_sending_time(sending_time):
	current_time = timezone.now()
	#sending_time = datetime.datetime(sending_time)
	print(sending_time)
	elapsed_time = str((current_time-sending_time)).split(':')
	print('ELAPSED TIME',elapsed_time)
	hour = int(elapsed_time[0])

	minute = elapsed_time[1]
	if minute != '00': # 00 -> int('')
		minute = int(minute.lstrip('0')) # 07 -> 7
	else:
		minute = 0

	second = elapsed_time[2].split('.')[0]
	if second != '00': # 00 -> int('')
		second = int(second.lstrip('0')) # 03.12345 --> 3
	else:
		second = 0

	#print(hour, minute, second)

	if hour == 0 and minute == 0 and second < 4:
		return 'éppen most'
	elif hour == 0 and minute == 0 and second >= 4:
		return f'{second} másodperce'
	elif hour == 0 and minute > 0:
		return f'{minute} perce'
	elif hour > 0:
		return f'{hour} órája'
	else:
		return 'ismeretlen küldési idő'



def create_sending_time(sending_time):
	"""
	Az üzenet küldési idejét számolja ki a következő módon:
		-> küldés adott napon: eltelt órák/percek/másodpercek száma
		-> küldés tegnap: küldési időpont
		-> küldés régebben: - küldés 7 napon belül: eltelt napok száma 
							- küldés 7 napnál régebben: dátum
	"""

	# example 3: https://www.programiz.com/python-programming/datetime/strftime


	if(naturalday(sending_time) == 'today'):
		message_time = format_today_messages_sending_time(sending_time)
	elif(naturalday(sending_time) == 'yesterday'):
		message_time = datetime.strftime(sending_time, '%H:%M')
		message_time = 'tegnap ' + str(message_time)
	else:
		message_time = format_older_messages_sending_time(sending_time)

	return message_time



@database_sync_to_async
def save_public_chat_room_message(user, room, message):
	"""
	Elküldött üzenet mentése az adatbázisba
	"""
	return PublicChatRoomMessage.objects.create(user=user, room=room, content=message)


@database_sync_to_async
def get_public_chat_room_messages(room, page_number):
	"""

	"""
	try:
		p = Paginator(PublicChatRoomMessage.objects.by_room(room), PUBLIC_CHAT_ROOM_MESSAGE_PAGE_SIZE)

		message = {}

		load_page_number = int(page_number)

		# elértük e az utolsó oldalt
		if load_page_number <= p.num_pages:
			load_page_number = load_page_number + 1
			s = EncodePublicChatRoomMessage()
			message['messages'] = s.serialize(p.page(page_number).object_list)
		else:
			message['messages'] = 'None'
		message['load_page_number'] = load_page_number

		# python szótár konvertálása JSON objektummá és visszatérés az értékkel

		return json.dumps(message)

	except Exception as exception:
		#print('get_chat: Something went wrong when getting PublicChatRoom messages')
		print(exception)
		return None


class EncodePublicChatRoomMessage(Serializer):
	def get_dump_object(self, object):
		"""
		PublicChatRoomMessage object szerializálása, mikor payload-ként küldjük a view-hoz
		JSON formátumra alakítjuk
		Függvény egy override
		"""

		message_obj = {
			'message_id'	: 	str(object.id),
			'message_type'	:	MESSAGE_TYPE_MESSAGE,
			'message'		:	str(object.content),
			'user_id'		:	str(object.user.id),
			'username'		:	str(object.user.username),
			'profile_image'	:  	str(object.user.profile_image.url),
			'sending_time'	:	create_sending_time(object.sending_time),
		}

		return message_obj
		


@database_sync_to_async
def add_user(room, user):
	"""
	Meghívja a modellben lévő add_user_to_current_users függvényt
	Ezzel hozzáférünk az adatbázis táblához:
		- mivel a hozzáférés szinkron művelet ezért át kell alakítani aszinkronná
	"""
	return room.add_user_to_current_users(user)


@database_sync_to_async
def remove_user(room, user):
	"""
	Meghívja a modellben lévő remove_user_from_current_users függvényt
	Ezzel hozzáférünk az adatbázis táblához:
		- mivel a hozzáférés szinkron művelet ezért át kell alakítani aszinkronná
	"""

	return room.remove_user_from_current_users(user)


