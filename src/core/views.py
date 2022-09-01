from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import *
from operator import attrgetter
from django.conf import settings

import json
from django.http import HttpResponse, JsonResponse

from core.constants import *
from team.models import Team

from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize


from account.utils import EncodeAccountObject, EncodeCharacterObject
from team.utils import EncodeTeamObject

@login_required(login_url='login')
def home_page_view(request):
	#user = Character.objects.get(account=request.user)
	#print(user.health_point, user.character_type)
	context = {} 

	user = Character.objects.get(account=request.user)

	context = {
		'user_id': user.account.id,
		'username': user.account.username,
		'strength': user.strength,
		'skill': user.skill,
		'intelligence': user.intelligence,
		'health_point': user.health_point,
		'fortune': user.fortune,
		'gold': user.gold,

	}

	return render(request, 'core/home_page.html', context)





def increase_attribute_value(request, *args, **kwargs):
	context = {}
	if request.method == 'POST':	
		user_id = request.POST.get('user_id')
		attr_type = request.POST.get('attribute_type')
		user = Character.objects.get(account=user_id)
		print('USERNAME ', user.account.username, ' ATTR ', attr_type)

		if (user.gold)- DEFAULT_ATTRIBUTE_INCREASE_VALUE >= 0: 
			if attr_type == 'strength':
				user.strength += 1
				user.gold -= DEFAULT_ATTRIBUTE_INCREASE_VALUE
				user.save()
				context['new_attr_value'] = str(user.strength)

			elif attr_type == 'skill':
				user.skill += 1
				user.gold -= DEFAULT_ATTRIBUTE_INCREASE_VALUE
				user.save()
				context['new_attr_value'] = str(user.skill)

			elif attr_type == 'intelligence':
				user.intelligence += 1
				user.gold -= DEFAULT_ATTRIBUTE_INCREASE_VALUE
				user.save()
				context['new_attr_value'] = str(user.intelligence)

			elif attr_type == 'health_point':
				user.health_point += 1
				user.gold -= DEFAULT_ATTRIBUTE_INCREASE_VALUE
				user.save()
				context['new_attr_value'] = str(user.health_point)


			elif attr_type == 'fortune':
				user.fortune += 1
				user.gold -= DEFAULT_ATTRIBUTE_INCREASE_VALUE
				user.save()
				context['new_attr_value'] = str(user.fortune)

			context['new_gold_value'] = str(user.gold)
			context['message'] = 'Success'
			context['attr_type'] = attr_type
		else: 
			context['message'] = 'Out of gold'


	return HttpResponse(json.dumps(context), content_type='application/json')


# beepitve mar a modellben, törlendo
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
	"""
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
	"""
	# EZ IS A MODELLBEN VAN MAR BEEPITVE
	#for character in characters:
		#dates_tmp.append(character.account.date_joined)
	#print(characters)

	characters = Character.objects.get_all_characters_in_ordered_list_without_admins()

	teams = Team.objects.all()

	context = {
		'characters': characters,
		'teams': teams,
		}


	#try_pagination()

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



def load_users_pagination(request):
	try:

		accounts = Character.objects.get_all_accounts_in_ordered_list_without_admins()

		characters = Character.objects.get_all_characters_in_ordered_list_without_admins()

		data = {}
		page_number = request.GET.get('page_number')

		load_page_number = int(page_number)

		print('PAGE NUMBER' + page_number)
		p = Paginator(characters, 8) # 8 azt jelenti hogy ennyi profilt jelenitunk meg egyszerre a felületen(8-esével)


		print('numpages', p.num_pages)

		if load_page_number <= p.num_pages:
			load_page_number = load_page_number + 1

			s = EncodeCharacterObject()

			print(s.serialize(p.page(page_number).object_list))
			print('next')

			data['users'] = s.serialize(p.page(page_number).object_list)
		else:
			data['users'] = 'None'

		data['load_page_number'] = load_page_number



		return JsonResponse(data)

	except Exception as exception:
		print('Error when getting users' + str(exception))

	return None


def load_teams_pagination(request):
	try:

		teams = Team.objects.all()

		data = {}
		page_number = request.GET.get('page_number')

		load_page_number = int(page_number)

		print('PAGE NUMBER' + page_number)
		p = Paginator(teams, 8) 


		print('numpages', p.num_pages)

		if load_page_number <= p.num_pages:
			load_page_number = load_page_number + 1

			s = EncodeTeamObject()

			print(s.serialize(p.page(page_number).object_list))
			print('next')
			print(load_page_number)

			data['teams'] = s.serialize(p.page(page_number).object_list)
		else:
			data['teams'] = 'None'

		data['load_page_number'] = load_page_number



		return JsonResponse(data)

	except Exception as exception:
		print('Error when getting users' + str(exception))

	return None


