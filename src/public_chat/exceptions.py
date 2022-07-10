import json
from functools import wraps
from .models import PublicChatRoom
from channels.db import database_sync_to_async


# https://gearheart.io/articles/creating-a-chat-with-django-channels/



class ClientError(Exception):
	"""
	Custom exception class that is caught by the websocket receive()
	handler and translated into a send back to the client.
	"""
	def __init__(self, code, message):
		super().__init__(code)
		self.code = code

		if message:
			self.message = message


@database_sync_to_async
def get_chat_room(room_id):
	try:
		room = PublicChatRoom.objects.get(pk=room_id)
	except PublicChatRoom.DoesNotExist:
		raise ClientError(422, 'ROOM_INVALID')

	return room


@database_sync_to_async
def handle_client_error(exception):
	"""
	ClientError kezelése
	"""
	
	error = {
		'error': exception.code,
		'message': 'Something went wrong',
	}

	if exception.message:
		error['message'] = exception.message

	#await self.send_json(error)

	return error