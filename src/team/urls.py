from django.urls import path

from team.views import (
	user_team_view,
	)

app_name = 'team'

urlpatterns = [
	path('', user_team_view, name='user_team_view'),
]