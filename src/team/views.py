from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.models import Account, Character
from .models import Team, Membership
from .forms import TeamCreationForm

import json
from django.http import HttpResponse, JsonResponse



# https://docs.djangoproject.com/en/4.0/topics/db/models/#extra-fields-on-many-to-many-relationships




@login_required(login_url='login')
def user_team_view(request):
	context = {}
	form = TeamCreationForm()
	context['form'] = form
	user = Account.objects.get(id=request.user.id)
	recent_user_id = user.id


	if request.method == 'POST':
		form = TeamCreationForm(request.POST)


		if form.is_valid():
			print('valid')
			try: 
				form.check_name_availability(request.POST.get('name')) # ellenorizzuk hogy a csapatnev nem szerepel e mar mas betukiosztasban(kis/nagy)
				team = form.save()
				Membership.objects.create(user=user, team=team)
				context['is_valid'] = True
				return redirect('team:user_team_view')
			except Exception as e:
				context['is_valid'] = False
				
		else:
			context['is_valid'] = False
			print('nem valid')

	else:
		context['is_valid'] = True
		#user = Account.objects.get(id=request.user.id)
		try:
			team_id = user.team_set.all()[0].id # admin felületen hozzá lehet adni egy usert több csapathoz is, viszont a webes felületen ezt nem engedjük
												# viszont emiatt mindig a "legelső" csapat számít, sose lesz több
		except:
			team_id = None

		if team_id:
			user_team = Team.objects.get(id=team_id)
			print(user_team.id, user_team.name, user_team.description)

			print('Csapattagok:', user_team.users.all())
			for user in user_team.users.all():
				print(user)

			print('USERID---', recent_user_id)
			context['has_team'] = True
			context['form'] = form
			context['user_id'] = recent_user_id
			context['team_id'] = user_team.id
			context['team_name'] = user_team.name
			context['team_description'] = user_team.description
			context['team_members'] = user_team.users.all()


		else:
			context['has_team'] = False
			context['form'] = form
			context['user_id'] = user.id


	teams = Team.objects.all()
	context['teams'] = teams

	return render(request, 'team/team_page.html', context)


def leave_team(request):
	context = {}
	user_id = request.POST.get('user_id')
	print('user_id' + user_id)
	user = Account.objects.get(id=user_id)
	print('felhasznalo' + user.username)
	try:
		team_id = user.team_set.all()[0].id
	except Exception as e:
		print(f'Team id not found for user {request.user} ' + str(e))
	try:
		user_team = Team.objects.get(id=team_id)
	except Exception as e:
		print(f'Team id not found in leave team ' + str(e))

	# errort dobhat ha a try utan except van
	print(user_team.name)
	print('leaving team')

	# felhasználó törlése a csapatból
	user_team.users.remove(user)

	# ha a csapatnak nincs több tagja, a csapat is törlődik
	if len(user_team.users.all()) == 0:
		Team.objects.get(id=team_id).delete()
		context['team_is_deleted'] = True
	else:
		context['team_is_deleted'] = False

	context['message'] = 'siker'

	return HttpResponse(json.dumps(context), content_type='application/json')


def join_team(request):
	context = {}

	user_id = request.POST.get('user_id')
	print('user_id ' + user_id)
	user = Account.objects.get(id=user_id)
	print('felhasznalo ' + user.username)

	team_id = request.POST.get('team_id')
	print('team_id ' + team_id)
	team = Team.objects.get(id=team_id)
	print('csapat ' + team.name)


	Membership.objects.create(user=user, team=team)

	context['message'] = 'siker'

	return HttpResponse(json.dumps(context), content_type='application/json')



def individual_team_view(request, *args, **kwargs):
	context = {}

	team_id = kwargs.get('team_id')

	try: 
		team = Team.objects.get(id=team_id)
	except Team.DoesNotExist:
		return HttpResponse('Team does not exists')

	user = Account.objects.get(id=request.user.id)

	# ellenőrizzük, hogy az adott csapatban benne van-e a user
	# ha nincs, akkor ellenőrizzük azt, hogy van-e csapata 
	has_team = True
	is_own_team = True
	try:
		team_membership = Membership.objects.get(user=user.id, team=team.id)
		print('csapattag')
	except Membership.DoesNotExist:
		print('nem csapattag')
		is_own_team = False
		try:
			membership = Membership.objects.get(user=user.id)
			print('van csapata')
		except Membership.DoesNotExist:
			print('nincs csapata')
			has_team = False



	context = {
		'team': team,
		'team_members': team.users.all(),
		'is_own_team': is_own_team,
		'has_team': has_team,
		'user_id': user.id,
	}


	return render(request, 'team/individual_team.html', context)