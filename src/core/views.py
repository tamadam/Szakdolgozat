from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import *
from operator import attrgetter
from django.conf import settings

import json
from django.http import JsonResponse


PUBLIC_CHAT_ROOM_ID = 1 # statikusan létrehozott ID, mivel ebből a szobából fixen 1 van


@login_required(login_url='login')
def home_page_view(request):
	#user = Character.objects.get(account=request.user)
	#print(user.health_point, user.character_type)
	context = {} 

	return render(request, 'core/home_page.html', context)


def get_all_characters_without_admins():
	"""
	users = Account.objects.exclude(is_admin=True)
	characters = []
	for user in users:
		characters.append(Character.objects.get(account=user))
	return characters
	"""

	return [Character.objects.get(account=user) for user in Account.objects.exclude(is_admin=True)]



@login_required(login_url='login')
def users_search_view(request):
	characters = get_all_characters_without_admins()

	#characters = sorted(characters, key=lambda character: character.level, reverse=True)
	# docs : https://wiki.python.org/moin/HowTo/Sorting#Sortingbykeys

	try:
		characters = sorted(characters, key=lambda character: character.account.date_joined) # először date szerint orderelünk
		characters = sorted(characters, key=attrgetter('honor','level'), reverse=True) # utana a mar rendezett listat honor és level szerint
	except:
		characters = sorted(characters, key=attrgetter('honor','level', 'account.username'), reverse=True)  # minimális az esély arra, hogy 2 felhasználó ms-re pontosan 
													# egyszerre regisztráljon, de ilyen esetben ez egy alternativ rendezési lehetőség,
													# a sorrend lényegén nem fog változtatni

	#for character in characters:
		#dates_tmp.append(character.account.date_joined)
	#print(characters)

	context = {'characters': characters}

	return render(request, 'core/search_users.html', context)

"""
def list_accounts(request):
	characters = Account.objects.exclude(is_admin=True)
	print(type(characters))
	context = {
		'characters': characters,
	}
	return JsonResponse({'characters': list(characters.values())})
"""

@login_required(login_url='login')
def public_chat_page_view(request):
	context = {
		'debug_mode': settings.DEBUG,
		'room_id': PUBLIC_CHAT_ROOM_ID, 
	}

	return render(request, 'core/public_chat_page.html', context)