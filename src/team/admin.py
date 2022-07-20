from django.contrib import admin
from account.models import Account
from .models import Team, Membership


class MembershipConfigInline(admin.TabularInline):
	model = Membership
	fields = ['user', 'date_joined']
	readonly_fields = fields
	extra = 0

	def has_add_permission(self, request, obj=None):
		return False
	
	def has_delete_permission(self, request, obj=None):
		return False



class TeamAdmin(admin.ModelAdmin):
	list_display = ['name', 'description', 'date_created']
	inlines = [MembershipConfigInline]
	readonly_fields = ['id']


class MembershipConfig(admin.ModelAdmin):
	list_display = ['user', 'team', 'date_joined']



admin.site.register(Team, TeamAdmin)
admin.site.register(Membership, MembershipConfig)