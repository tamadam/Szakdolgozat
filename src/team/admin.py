from django.contrib import admin
from account.models import Account
from .models import Team, Membership


class MembershipConfig(admin.TabularInline):
	model = Membership
	extra = 0

class TeamAdmin(admin.ModelAdmin):
	list_display = ['name', 'description']
	inlines = [MembershipConfig]


admin.site.register(Team, TeamAdmin)
admin.site.register(Membership)