from django.urls import path

from account.views import (
	edit_profile_view,
	validate_username_realtime,
	validate_email_realtime,
	validate_password_realtime,
	)

app_name = 'account'

urlpatterns = [
	path('edit/<user_id>', edit_profile_view, name='edit'),
	path('validate_username_realtime', validate_username_realtime, name='validate_username_realtime'),
	path('validate_email_realtime', validate_email_realtime, name='validate_email_realtime'),
	path('validate_password_realtime', validate_password_realtime, name='validate_password_realtime'),
]