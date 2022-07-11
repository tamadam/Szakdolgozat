from django.urls import path

from account.views import (
	edit_profile_view,
	)

app_name = 'account'

urlpatterns = [
	path('edit/<user_id>', edit_profile_view, name='edit'),
]