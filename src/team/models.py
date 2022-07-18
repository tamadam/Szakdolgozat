from django.db import models
from django.conf import settings



class Team(models.Model):

	name 			= models.CharField(max_length=60, unique=True, blank=False)
	description 	= models.TextField(max_length=200, unique=False, blank=True, default="Csapatleírás")
	#users 			= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='user_team')
	

	def __str__(self):
		return self.name



