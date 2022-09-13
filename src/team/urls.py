from django.urls import path

from team.views import (
	user_team_view,
	leave_team,
	join_team,
	individual_team_view,
	save_team_description,
	)

app_name = 'team'

urlpatterns = [
	path('', user_team_view, name='user_team_view'),
	path('leave_team/', leave_team, name='leave_team'),
	path('join_team/', join_team, name='join_team'),
	path('<team_id>/', individual_team_view, name='individual_team_view'),
	path('save_team_description', save_team_description, name='save_team_description'),
]