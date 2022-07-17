from django.shortcuts import render, redirect
from .models import *
from .forms import AccountRegistrationForm, AccountEditForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .decorators import anonymous_user

from django.views.generic import ListView
import json

from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from core.constants import STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET
from django.conf import settings 
import os

@anonymous_user
def register_page_view(request):
	form = AccountRegistrationForm()

	if request.method == 'POST':
		form = AccountRegistrationForm(request.POST)

		if form.is_valid():
			user = form.save()
			character_type = form.cleaned_data.get('character_type')
			if character_type == Character.ROLES[0][0]: #'warrior'
				set_warrior(user)
			elif character_type == Character.ROLES[1][0]: # 'mage'
				set_mage(user)
			elif character_type == Character.ROLES[2][0]:# 'scout'
				set_scout(user)
			else:
				pass # admin user has the default values

			return redirect('login')



	context = {'form':form}

	return render(request, 'account/register.html', context)


@anonymous_user
def login_page_view(request):

	if request.method == 'POST':
		username = request.POST['username'] # input name-ből jön
		password = request.POST['password']

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('home_page')
		else:
			messages.info(request, 'Invalid creditentals')


	context = {}

	return render(request, 'account/login.html', context)

@login_required(login_url='login')
def logout_view(request):
	logout(request)

	return redirect('login')


@login_required(login_url='login')
def profile_view(request, *args, **kwargs):
	context = {}

	user_id = kwargs.get('user_id')
	try:
		account = Account.objects.get(id=user_id)
	except Account.DoesNotExist:
		return HttpResponse('Account does not exist')

	owner_of_the_profile = False

	if request.user.id == account.id: 
		owner_of_the_profile = True

	context = {
		'username': account.username,
		'user_id': account.id,
		'level': account.character.level,
		'strength': account.character.strength,
		#'profile_image': account.profile_image.url,
		'character_type': account.character.character_type,
		'is_owner': owner_of_the_profile,
		'gold': account.character.gold,
	}

	# ha az adott felhasználói profilnak van profilképe állítsa be amúgy az alap
	if account.profile_image:
		context['profile_image'] = account.profile_image.url
		#print(account.get_profile_image_filename())
	else:
		context['profile_image'] = STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET




	

	return render(request, 'account/profile.html', context)


@login_required(login_url='login')
def edit_profile_view(request, *args, **kwargs):
	context = {}
	#print(','.join('{0}={1!r}'.format(k,v) for k,v in kwargs.items()))
	user_id = kwargs.get('user_id')

	try:
		account = Account.objects.get(id=user_id)
	except Account.DoesNotExist:
		return HttpResponse('Account does not exist')

	if request.user.id != account.id:
		return HttpResponse('You are not allowed to edit other players profile')


	# itt már biztosan mi akarjuk szerkeszteni a profilunkat
	
	form = AccountEditForm(instance=account)

	if request.method == 'POST':
		form = AccountEditForm(request.POST, request.FILES, instance=account)
		if form.is_valid():
			form.save()
			return redirect('profile', user_id=account.id)

	context = {
		'form': form,
	}

	return render(request, 'account/edit_profile.html', context)






def set_warrior(user):
	profile = Character.objects.get(account=user)

	profile.character_type = Character.ROLES[0][0]

	#re-define attribute values based on role type
	profile.strength = 10
	profile.skill = 5
	profile.intelligence = 5
	profile.health_point = 12
	profile.fortune = 7



	profile.save()


def set_mage(user):
	profile = Character.objects.get(account=user)

	profile.character_type = Character.ROLES[1][0]

	#re-define attribute values based on role type
	profile.strength = 6
	profile.skill = 5
	profile.intelligence = 12
	profile.health_point = 8
	profile.fortune = 6

	profile.save()


def set_scout(user):
	profile = Character.objects.get(account=user)

	profile.character_type =  Character.ROLES[2][0]

	#re-define attribute values based on role type
	profile.strength = 7
	profile.skill = 11
	profile.intelligence = 7
	profile.health_point = 9
	profile.fortune = 8

	profile.save()