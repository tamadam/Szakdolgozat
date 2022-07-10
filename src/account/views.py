from django.shortcuts import render, redirect
from .models import *
from .forms import AccountRegistrationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .decorators import anonymous_user

from django.views.generic import ListView
import json

from django.http import HttpResponse
from django.contrib import messages


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


def profile_view(request, *args, **kwargs):
	context = {}
	user_id = kwargs.get('user_id')
	try:
		account = Character.objects.get(account=user_id)
	except Character.DoesNotExist:
		return HttpResponse('Account does not exist')

	if account:
		context = {
			'username': account.account.username,
			'character_type': account.character_type,
			'user_id': account.account.id,
			'level': account.level,
			'strength': account.strength,
			'profile_image': account.account.profile_image.url
		}


	owner_of_the_profile = True
	current_user = request.user

	if current_user.is_authenticated and current_user != account.account: #account.account mivel characterbol hivatkozunk a accountra
		owner_of_the_profile = False
	elif not current_user.is_authenticated:
		owner_of_the_profile = False

	context['is_owner'] = owner_of_the_profile

	return render(request, 'account/profile.html', context)


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