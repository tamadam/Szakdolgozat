from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def user_team_view(request):
	context = {}

	return render(request, 'team/team_page.html', context)