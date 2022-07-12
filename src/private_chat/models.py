from django.db import models
from django.conf import settings



class PrivateChatRoom(models.Model):
	"""
	Privát chat szoba felépítése
	"""
	user1			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1')
	user2			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2')

	def __str__(self):
		return f'Private chat between {self.user1} and {self.user2}'


	@property
	def group_name(self):
		return f'PrivateChatRoom_{self.id}'


class PrivateChatRoomMessageManager(models.Manager):
	def get_chat_messages_by_room(self, room):
		qs = PrivateChatRoomMessage.objects.filter(room=room).order_by('-sending_time')


class PrivateChatRoomMessage(models.Model):
	"""
	Üzenet a PrivateChatRoomban
	"""
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	room 			= models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
	sending_time	= models.DateTimeField(auto_now_add=True)
	content 		= models.TextField(unique=False, blank=False)


	objects = PrivateChatRoomMessageManager()


	def __str__(self):
		return self.content