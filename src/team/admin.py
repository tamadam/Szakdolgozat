from django.contrib import admin

from account.models import Account
from .models import Team


# https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.InlineModelAdmin.get_extra
# https://stackoverflow.com/questions/37338925/django-tabularinline-discard-empty-rows

class AccountInLine(admin.TabularInline):
	model = Account
	fields  = ['username', 'email']
	readonly_fields = fields
	extra = 0

class TeamAdminConfig(admin.ModelAdmin):
	inlines = [
		AccountInLine,
	]
	list_display = ['id','name', 'description']
	search_fields = ['id', 'name']

	class Meta:
		model = Team

admin.site.register(Team, TeamAdminConfig)


"""
class AccountInLine(admin.TabularInline):
	model = Account


class TeamAdminConfig(admin.ModelAdmin):
	inlines = [
		AccountInLine,
	]
	list_display = ['id','name', 'description']
	search_fields = ['id', 'name']

	class Meta:
		model = Team

admin.site.register(Team, TeamAdminConfig)
"""
