from django.urls import path

from game.views import (
	game_choice_view,
	easy_game_view,
	medium_game_view,
	hard_game_view,
	finished_game,
	arena_view,
	arena_fight,
	)

app_name = 'game'

urlpatterns = [
	path('', game_choice_view, name='game_choice'),
	path('konnyu/', easy_game_view, name='easy_game'),
	path('kozepes/', medium_game_view, name='medium_game'),
	path('nehez/', hard_game_view, name='hard_game'),
	path('finished_game',finished_game, name='finished_game'),
	path('arena/', arena_view, name='arena'),
	path('arena_fight', arena_fight, name='arena_fight'),
]