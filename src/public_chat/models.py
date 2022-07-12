from django.db import models
from django.conf import settings


class PublicChatRoom(models.Model):
	"""
	A publikus chat szoba felépítése
	"""
	name 		= models.CharField(max_length=60, unique=True, blank=False) #name must be set

	users 		= models.ManyToManyField(settings.AUTH_USER_MODEL, blank = True) # users who are connected to the chat


	def __str__(self):
		return self.name


	def add_user_to_current_users(self, user):
		"""
		Amikor egy felhasználó csatlakozik egy szobához, és ezáltal egy sockethez, ez a függvény fog meghívódni
		Visszatérési értéke: igaz, hogyha a felhasználó hozzá lett adva a users listához
		Megj.: users lista a chatszobában jelenleg csatlakozott felhasználók listája
		"""
		if not user in self.users.all():
			self.users.add(user)
			self.save()
			print(f'{user.username} ONLINE')


	def remove_user_from_current_users(self, user):
		"""
		Amikor egy felhasználó elhagyja a chatszobát, és ezáltal bezárja a socketet
		Visszatérési értéke: igaz, hogyha a felhasználó el lett távolítva a users listából
		"""
		if user in self.users.all():
			self.users.remove(user)
			self.save()
			print(f'{user.username} OFFLINE')



	@property
	def group_name(self):
		"""
		Group: channeleknek a kollekciója; channelek: maguk a userek 
		Visszatérési értéke egy név, amelyre tudnak csatlakozni, ezáltal megkapják az elküldött üzeneteket
		"""
		return f'MainRoom_ID_{self.id}'



class PublicChatRoomMessageManager(models.Manager):
	def get_chat_messages_by_room(self, room):
		"""
		Adott szobában lévő összes chat üzenet lekérdezése
		"""
		qs = PublicChatRoomMessage.objects.filter(room=room).order_by("-sending_time")

		return qs
	

class PublicChatRoomMessage(models.Model):
	"""
	Üzenet a PublicChatRoomban
	"""
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # ha egy user torlodik a chat uzenetei is
	room 			= models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE) # ha a chatszoba törlődik az összes ebben lévő üzenet is
	sending_time 	= models.DateTimeField(auto_now_add=True)
	content 		= models.TextField(unique=False, blank=False)

	objects = PublicChatRoomMessageManager()


	def __str__(self):
		return self.content

