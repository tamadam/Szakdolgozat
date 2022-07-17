from django.urls import path

from core.views import (
	increase_attribute_value
	)

app_name = 'core'

urlpatterns = [
	#path('list_accounts', list_accounts, name='list_accounts'),
	path('increase_attribute_value/', increase_attribute_value, name='increase_attribute_value'),
]