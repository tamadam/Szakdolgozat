from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.conf import settings


class Notification(models.Model):

	# felhasználó akinek küldjük az értesítést
	notified_user 		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	# felhasználó akitől jön az értesítés
	sender_user 		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sender_user')

	# az adott értesítésre kattintva elirányít a megfelelő helyre
	notification_url 	= models.URLField(max_length=350, null=True, unique=False, blank=True)

	# leírja az értesítés tartalmát (pl xy uzenetet küldott neked)
	verb	 			= models.CharField(max_length=100, unique=False, blank=True, null=True)

	sending_time 		= models.DateTimeField(auto_now_add=True)

	# számon tartja melyek azok az értesítések amelyeket a felhasználó már látott vagy nem
	read 				= models.BooleanField(default=False)


	# generic type

	content_type 		= models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id 			= models.PositiveIntegerField()
	content_object 		= GenericForeignKey()


	def __str__(self):
		return self.verb


	def get_content_object_type(self):
		"""
		Minden olyan tábla amely értesítést tud generálni, lesz egy get_cname fuggvenye
		visszatérési értéke a tábla neve
		a javascripthez lesz hasznos mikor kiepitjuk a notificationoket a menuben
		"""
		return str(self.content_object.get_cname)