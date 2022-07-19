from django.db import models
from django.conf import settings

# https://docs.djangoproject.com/en/4.0/topics/db/models/#extra-fields-on-many-to-many-relationships

class Team(models.Model):
	name 			= models.CharField(max_length=60, unique=True, blank=False)
	description		= models.TextField(max_length=200, unique=False, blank=True, default="Leírás")
	users 			= models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='users')


	def __str__(self):
		return self.name


class Membership(models.Model):
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	team 			= models.ForeignKey(Team, on_delete=models.CASCADE)
	date_joined 	= models.DateField()


	class Meta:
		unique_together = [['user', 'team']] # pl magust ne lehessen 2x beletenni egy csapatba

	def __str__(self):
		return (f'{self.user.username} in {self.team.name}')