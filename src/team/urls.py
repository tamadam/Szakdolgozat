from django.urls import path

from team.views import (
	user_team_view,
	leave_team,
	)

app_name = 'team'

urlpatterns = [
	path('', user_team_view, name='user_team_view'),
	path('leave_team/', leave_team, name='leave_team'),
]