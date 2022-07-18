from django.shortcuts import render
from account.models import Character, Account
from team.models import Team
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def user_team_view(request):
	context = {}
	user = Account.objects.get(id=request.user.id) # felhasznalo
	try:
		team = Team.objects.get(id=user.team.id) #csapata
	except:
		team = None

	if team:
		team_id = team.id
		team_name = team.name 
		team_description = team.description

		team_mates = Account.objects.filter(team=team_id)
		for teammate in team_mates:
			print(teammate.username)

		
		context = {
			'has_team': True,
			'team_id': team_id,
			'team_name': team_name,
			'team_description': team_description,
			'team_mates': team_mates,
		}
	else:
		context['has_team'] = False

	return render(request, 'team/team_page.html', context)