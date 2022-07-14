from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import *
from operator import attrgetter
from django.conf import settings


PUBLIC_CHAT_ROOM_ID = 1 # statikusan létrehozott ID, mivel ebből a szobából fixen 1 van


@login_required(login_url='login')
def home_page_view(request):
	#user = Character.objects.get(account=request.user)
	#print(user.health_point, user.character_type)
	context = {} 

	return render(request, 'core/home_page.html', context)


@login_required(login_url='login')
def users_search_view(request):
	users = Account.objects.all()
	characters = []
	for user in users:
		if not user.is_admin:
			characters.append(Character.objects.get(account=user))

	#characters = sorted(characters, key=lambda character: character.level, reverse=True)
	# docs : https://wiki.python.org/moin/HowTo/Sorting#Sortingbykeys
	characters = sorted(characters, key=attrgetter('honor','level','account.username'), reverse=True)
	#for character in characters:
	#	print(character.level)

	#print(characters)

	context = {'characters': characters}

	return render(request, 'core/search_users.html', context)


@login_required(login_url='login')
def public_chat_page_view(request):
	context = {
		'debug_mode': settings.DEBUG,
		'room_id': PUBLIC_CHAT_ROOM_ID, 
	}

	return render(request, 'core/public_chat_page.html', context)