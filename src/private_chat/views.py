from django.shortcuts import render
from django.conf import settings

from .models import *
from account.models import Account
from django.contrib.auth.decorators import login_required

from itertools import chain
from core.constants import *


from private_chat.utils import create_or_get_private_chat
import json
from django.http import HttpResponse


@login_required(login_url='login')
def private_chat_page_view(request, *args, **kwargs):

	user = request.user

	# Összes szoba amiben a felhasználó benne van
	rooms_parameter_user1 = PrivateChatRoom.objects.filter(user1=user)
	rooms_parameter_user2 = PrivateChatRoom.objects.filter(user2=user)

	rooms = list(chain(rooms_parameter_user1, rooms_parameter_user2)) # mergeli és eltávolítja a duplikált elemeket

	#[{'message:' 'mizu', 'user': 'tamadam'}, {'message:' 'semmi kul', 'user': 'harcos'}]
	messages_and_users = []
	users = []
	for room in rooms:
		if room.user1 == user:
			other_user = room.user2
		else:
			other_user = room.user1

		try:
			profile_image = other_user.profile_image.url
		except Exception as e:
			profile_image = STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET


		messages_and_users.append({
				'message': '',
				'other_user': other_user,
				'profile_image': profile_image,
			})


	context = {
		'debug_mode': settings.DEBUG,
		'messages_and_users': messages_and_users,
	}


	return render(request, 'private_chat/room.html', context)


@login_required(login_url='login')
def create_or_return_private_chat(request, *args, **kwargs):
	user1 = request.user
	context = {}
	if user1.is_authenticated:
		if request.method == 'POST':
			user2_id = request.POST.get('user2_id')
			try:
				user2 = Account.objects.get(id=user2_id)
				chat = create_or_get_private_chat(user1, user2)
				context['message'] = 'Got your private chat'
				context['private_chat_room_id'] = chat.id
			except Account.DoesNotExist:
				payload['message'] = 'Error when getting private chat'
	else:
		payload['message']: 'Authentication failure'

	return HttpResponse(json.dumps(context), content_type='application/json')