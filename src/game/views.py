from django.shortcuts import render
from account.models import Account, Character, CharacterHistory

from game.models import Arena

from django.http import JsonResponse
from core.constants import *
import math

from django.core import serializers
import json

from account.utils import EncodeAccountObject


def easy_game_view(request):
	context = {}

	user = Account.objects.get(id=request.user.id)

	context = {
		'user_id': user.id,
	}

	return render(request, 'game/easy_game.html', context)


def medium_game_view(request):
	context = {}

	user = Account.objects.get(id=request.user.id)

	context = {
		'user_id': user.id,
	}

	return render(request, 'game/medium_game.html', context)



def hard_game_view(request):
	context = {}

	user = Account.objects.get(id=request.user.id)

	context = {
		'user_id': user.id,
	}

	return render(request, 'game/hard_game.html', context)



def increase_attributes_on_level_up(character):
	"""
	Szintlépéskor az összes tulajdonság értéke 8%-al nő
	"""
	character.strength = math.ceil(float(character.strength) * DEFAULT_ATTRIBUTE_INCREASE_PERCENTAGE)
	character.skill = math.ceil(float(character.skill) * DEFAULT_ATTRIBUTE_INCREASE_PERCENTAGE)
	character.intelligence = math.ceil(float(character.intelligence) * DEFAULT_ATTRIBUTE_INCREASE_PERCENTAGE)
	character.health_point = math.ceil(float(character.health_point) * DEFAULT_ATTRIBUTE_INCREASE_PERCENTAGE)
	character.fortune = math.ceil(float(character.fortune) * DEFAULT_ATTRIBUTE_INCREASE_PERCENTAGE)
	#print(math.ceil(float(character.strength) * DEFAULT_ATTRIBUTE_INCREASE_PERCENTAGE))



def finished_game(request):
	data = {}
	user_id = None
	game_type = 'easy'

	try:
		user_id=request.GET.get('user_id')
		game_type=request.GET.get('game_type')
	except Exception as e:
		print(e)
		pass

	if user_id:
		character = Character.objects.get(account=user_id)

		# játék fajták megkülönböztetése --> mindegyikért eltérő mennyiségű XP jár
		if game_type == 'easy':
			character.current_xp += DEFAULT_XP_INCREASE_EASY_GAME
			character.gold += DEFAULT_GOLD_INCREASE_EASY_GAME
		elif game_type == 'medium':
			character.current_xp += DEFAULT_XP_INCREASE_MEDIUM_GAME
			character.gold += DEFAULT_GOLD_INCREASE_MEDIUM_GAME
		elif game_type == 'hard':
			character.current_xp += DEFAULT_XP_INCREASE_HARD_GAME
			character.gold += DEFAULT_GOLD_INCREASE_HARD_GAME

		# szintlépés, ilyenkor növekszik a szint 1-el, az xp 0-zódik, az elérendő xp növekszik az előzőhöz képest, és a tulajdonsagok is nonek
		if character.current_xp >= character.next_level_xp:
			character.level += 1
			character.current_xp = 0
			character.next_level_xp += DEFAULT_NEXT_LEVEL_XP_INCREASE
			increase_attributes_on_level_up(character)

		character.save()

	data = {
		'message': 'Success',
	}

	return JsonResponse(data)



def arena_view(request):
	context = {}

	user_to_attack_id = request.GET.get(('ellenfel_id')) # a profilon keresztül
	user_id = request.user.id # a támadó user
	current_character = Character.objects.get(account=user_id)

	if user_to_attack_id:
		try:
			user_to_attack = Character.objects.get(account=user_to_attack_id)
		except:
			user_to_attack = None
			pass

		context = {
			'left_character': '',
			'left_character_id': '',
			'right_character': '',
			'right_character_id': '',
			'current_character': current_character,
			'current_character_id': current_character.account.id,
			'is_user_to_attack': True,
			'user_to_attack_id': user_to_attack_id,
			'user_to_attack': user_to_attack,
		}
	else:
		characters = Character.objects.get_all_characters_in_ordered_list_without_admins()


		characters_count = len(characters)
		current_character_index = None
		left_side = None
		right_side = None
		left_side_id = None
		right_side_id = None
		# az adminok nem lesznek benne
		if current_character in characters:
			for i, value in enumerate(characters):
				if current_character == value:
					current_character_index = i
			# legalább 3 karakternek lennie kell az arénához
			if characters_count >= 3:
				if current_character_index is not None:
					if current_character_index == 0:
						# ha 0, akkor ő az első, ezért a két mögötte lévőt tesszük az arénába
						left_side = characters[current_character_index + 1] 
						right_side = characters[current_character_index + 2]

					elif current_character_index == characters_count - 1:
						# ha characters_count - 1-el egyenlő, azt jelenti, ő az utolsó, a két előtte lévőt kérjük
						left_side = characters[current_character_index - 1]
						right_side = characters[current_character_index - 2]

					else:
						# ha se nem első, se nem utolsó, akkor van egy előtte és utána lévő, ezeket tesszük az arénába
						left_side = characters[current_character_index + 1]
						right_side = characters[current_character_index - 1]

					#print(left_side, right_side)
					left_side_id = left_side.account.id
					right_side_id = right_side.account.id
					#print("IDK: ", left_side_id, right_side_id)
				else:
					# ha valamiért a current_character_index None, akkor csak menjen tovább a program
					# elvileg ez sem lehetséges
					pass
			else:
				# ha csak 1 vagy 2 karakter van akkor mi történjen
				# ha 0 karakter van, akkor csak az admin léphet be, viszont azt már fentebb lekezeljük
				# így nem fordulhat elő, hogy ide jusson a program, hogyha nincs karakter
				pass


		else:
			# adminoknak mi történjen
			pass

		context = {
			'left_character': left_side,
			'left_character_id': left_side_id,
			'right_character': right_side,
			'right_character_id': right_side_id,
			'current_character': current_character,
			'current_character_id': current_character.account.id,
			'is_user_to_attack': False,
		}


	return render(request, 'game/arena.html', context)


def decide_winner(attacker, defender):
	attacker_role = attacker.character_type
	attacker_health = attacker.health_point * 30
	#attacker_luck_value = attacker.fortune
	
	defender_role = defender.character_type
	defender_health = defender.health_point * 30
	#defender_luck_value = defender.fortune

	attacker_health_value_list = []
	defender_health_value_list = []
	attacker_health_value_list.append(attacker_health)
	defender_health_value_list.append(defender_health)

	print('KEZDO ÉLETERO: ATTACKER - DEFENDER', attacker_health, defender_health)

	# a casthoz tartozó fő tulajdonságok meghatározása
	"""
	harcos - harcos
	harcos - mágus
	harcos - íjász
	mágus - mágus
	mágus - íjász
	íjász - íjász


	mágus - harcos
	íjász - harcos
	íjász - mágus
	"""
	if attacker_role == 'warrior' and defender_role == 'warrior':
		attacker_main_attr_value = attacker.strength
		defender_main_attr_value = defender.strength
		attacker_protect_attr_value = 0
		defender_protect_attr_value = 0

	elif attacker_role == 'warrior' and defender_role == 'mage':
		attacker_main_attr_value = attacker.strength
		defender_main_attr_value = defender.intelligence
		attacker_protect_attr_value = attacker.intelligence
		defender_protect_attr_value = defender.strength

	elif attacker_role == 'warrior' and defender_role == 'scout':
		attacker_main_attr_value = attacker.strength
		defender_main_attr_value = defender.skill
		attacker_protect_attr_value = attacker.skill
		defender_protect_attr_value = defender.strength

	elif attacker_role == 'mage' and defender_role == 'mage':
		attacker_main_attr_value = attacker.intelligence
		defender_main_attr_value = defender.intelligence
		attacker_protect_attr_value = 0
		defender_protect_attr_value = 0

	elif attacker_role == 'mage' and defender_role == 'scout':
		attacker_main_attr_value = attacker.intelligence
		defender_main_attr_value = defender.skill
		attacker_protect_attr_value = attacker.skill
		defender_protect_attr_value = defender.intelligence

	elif attacker_role == 'scout' and defender_role == 'scout':
		attacker_main_attr_value = attacker.skill
		defender_main_attr_value = defender.skill
		attacker_protect_attr_value = 0
		defender_protect_attr_value = 0

	elif attacker_role == 'mage' and defender_role == 'warrior':
		attacker_main_attr_value = attacker.intelligence
		defender_main_attr_value = defender.strength
		attacker_protect_attr_value = attacker.strength
		defender_protect_attr_value = defender.intelligence

	elif attacker_role == 'scout' and defender_role == 'warrior':
		attacker_main_attr_value = attacker.skill
		defender_main_attr_value = defender.strength
		attacker_protect_attr_value = attacker.strength
		defender_protect_attr_value = defender.skill

	elif attacker_role == 'scout' and defender_role == 'mage':
		attacker_main_attr_value = attacker.skill
		defender_main_attr_value = defender.intelligence
		attacker_protect_attr_value = attacker.intelligence
		defender_protect_attr_value = defender.skill


	did_attacker_win = False

	
	while True:
		# mindig a támadó kezd tehát mindig a védekező sérül először
		defender_health -= attacker_main_attr_value * 10



		if defender_health <= 0:
			defender_health_value_list.append('0')
			did_attacker_win = True
			break

		defender_health_value_list.append(defender_health)

		# ha nem halt meg a védekező, akkor ő jön, a támadó sebződik

		attacker_health -= defender_main_attr_value * 10


		if attacker_health <= 0:
			attacker_health_value_list.append('0')
			break


		attacker_health_value_list.append(attacker_health)
		#print('DEF HEALTH', defender_health)
		#print('ATTACK HEALTH', attacker_health)


	#print('ATTACKER HEALTH LIST', attacker_health_value_list)
	#print('DEFENDER_HEALTH_LIST', defender_health_value_list)

	if did_attacker_win:
		return attacker, attacker_health_value_list, defender_health_value_list

	return defender, attacker_health_value_list, defender_health_value_list



def arena_fight(request):
	data = {}


	attacker_user_id = None
	defender_user_id = None

	user_win = None

	try:
		attacker_user_id=request.GET.get('attacker_user_id')
		defender_user_id=request.GET.get('defender_user_id')
	except Exception as e:
		print(e)
		pass


	attacker_user = Character.objects.get(account=attacker_user_id)
	defender_user = Character.objects.get(account=defender_user_id)


	winner, attacker_health_values, defender_health_values = decide_winner(attacker_user, defender_user)

	attacker_user_history = CharacterHistory.objects.get(account=attacker_user_id)
	defender_user_history = CharacterHistory.objects.get(account=defender_user_id)

	attacker_user_history.fights_played += 1
	defender_user_history.fights_played += 1


	#add arena matches
	Arena.objects.create_arena_match(attacker_user, defender_user, 	json.dumps([int(num) for num in attacker_health_values]), json.dumps([int(num) for num in defender_health_values]), winner)



	print('hey')
	#print(json.dumps(attacker_health_values))
	print('ho')

	print('GYŐZTES', winner)
	serialized_winner = serializers.serialize('json', [winner.account])
	print('ATTACKER', attacker_health_values)
	print('DEFENDER', defender_health_values)
	print(type(attacker_health_values))
	if winner == attacker_user:
		user_win = 'attacker'

		# becsületpont
		attacker_user.honor += 20
		defender_user.honor -= 20
		if defender_user.honor < 0:
			defender_user.honor = 0

		# statisztika
		attacker_user_history.fights_won += 1
		defender_user_history.fights_lost += 1
	elif winner == defender_user:
		user_win = 'defender'


		defender_user.honor += 20
		attacker_user.honor -= 20
		if attacker_user.honor < 0:
			attacker_user.honor = 0


		defender_user_history.fights_won += 1	
		attacker_user_history.fights_lost += 1


	attacker_user_history.save()
	attacker_user.save()
	defender_user.save()
	defender_user_history.save()


	s = EncodeAccountObject()

	account_object = {}
	account_object['winner_id'] = s.serialize([winner.account])[0]
	#print(json.loads(json.dumps(account_object['winner_id'])))
	data = {
		'message': 'Success',
		'attacker_health_values': attacker_health_values,
		'defender_health_values': defender_health_values,
		'user_win': account_object['winner_id'], #átadjuk az account objectet jsonre serializaljuk eloszor
	}

	return JsonResponse(data)