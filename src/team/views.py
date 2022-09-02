from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.models import Account, Character
from .models import Team, Membership, TeamMessage
from .forms import TeamCreationForm
from django.conf import settings
import json

from core.constants import *

from django.http import HttpResponse, JsonResponse



# https://docs.djangoproject.com/en/4.0/topics/db/models/#extra-fields-on-many-to-many-relationships




@login_required(login_url='login')
def user_team_view(request):
	print('USER TEAM VIEW')
	context = {}
	form = TeamCreationForm()
	context['form'] = form
	user = Account.objects.get(id=request.user.id)
	recent_user_id = user.id # user a későbbiekben megváltozik, ezért itt el kell menteni


	if request.method == 'POST':
		form = TeamCreationForm(request.POST)

		if form.is_valid():
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

	else:
		print('else')
		context['is_valid'] = True
		#user = Account.objects.get(id=request.user.id)
		try:
			team_id = user.team_set.all()[0].id # admin felületen hozzá lehet adni egy usert több csapathoz is, viszont a webes felületen ezt nem engedjük
												# viszont emiatt mindig a "legelső" csapat számít, sose lesz több
		except:
			team_id = None

		if team_id:
			print('van id')
			user_team = Team.objects.get(id=team_id)
			print(user_team.id, user_team.name, user_team.description)

			for user in user_team.users.all():
				print(user)

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

	update_team_rank()

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
	#print('user_id ' + user_id)
	user = Account.objects.get(id=user_id)
	#print('felhasznalo ' + user.username)

	team_id = request.POST.get('team_id')
	#print('team_id ' + team_id)
	team = Team.objects.get(id=team_id)
	#print('csapat ' + team.name)


	Membership.objects.create(user=user, team=team)

	context['message'] = 'siker'

	return HttpResponse(json.dumps(context), content_type='application/json')


@login_required(login_url='login')
def individual_team_view(request, *args, **kwargs):
	context = {}


	team_id = kwargs.get('team_id')

	try: 
		team = Team.objects.get(id=team_id)
	except Team.DoesNotExist:
		return HttpResponse('Team does not exists')
	try:
		user = Account.objects.get(id=request.user.id)
	except Account.DoesNotExist:
		return HttpResponse('Account does not exists')

	# ellenőrizzük, hogy az adott csapatban benne van-e a user
	# ha nincs, akkor ellenőrizzük azt, hogy van-e csapata 
	has_team = True
	is_own_team = True
	try:
		team_membership = Membership.objects.get(user=user.id, team=team.id)
		#print('csapattag')
	except Membership.DoesNotExist:
		#print('nem csapattag')
		is_own_team = False
		try:
			membership = Membership.objects.get(user=user.id)
			#print('van csapata')
		except Membership.DoesNotExist:
			#print('nincs csapata')
			has_team = False

	try:
		account = Account.objects.get(id=request.user.id)
	except:
		account = None
		pass


	team_members = []
	for team_member in team.users.all():
		print("csapattag", team_member)

		try:
			profile_image = team_member.profile_image.url
		except Exception as e:
			profile_image = STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET

		team_members.append({
				'member': team_member,
				'member_profile_image': profile_image,
			})


	context = {
		'team': team,
		'team_members': team_members,
		'is_own_team': is_own_team,
		'has_team': has_team,
		'user_id': user.id,
		'account': account,
	}

	# CHAT RÉSZ ------------------------

	context['debug_mode'] = settings.DEBUG


	return render(request, 'team/individual_team.html', context)




def update_team_rank():
	print('updating team ranks...')
	rank_counter = 1
	teams = Team.objects.all()
	teams = sorted(teams, key=lambda team: team.date_created)

	for team in teams:
		team.rank = rank_counter
		rank_counter += 1
		team.save()