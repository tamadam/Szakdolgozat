from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model


from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver	

class CustomAccountManager(BaseUserManager):
	# what happens when we create a new user
	def create_user(self, username, email, password, **other_fields):
		# validation checks
		if not email:
			raise ValueError('You must have an email address')

		if not username:
			raise ValueError('You must have an username')

		user = self.model(
				email = self.normalize_email(email),
				username = username,
			)



		user.set_password(password)
		user.save()

		return user


	#what happens when we create a new superuser
	def create_superuser(self, username, email, password, **other_fields):
		user = self.create_user(
				email = self.normalize_email(email),
				username = username,
				password=password,
			)
		user.is_admin=True
		user.is_staff=True
		user.is_superuser=True
		user.save()

		return user



def profile_image_path(self, filename): #self, filename
	return f'profile_images/{self.pk}/{"profile_image.png"}'


def default_profile_image():
	return 'images/logo_1080_1080.png'



class Account(AbstractBaseUser):
	# general info
	username		= models.CharField(verbose_name = 'username', max_length = 20, unique = True)
	email 			= models.EmailField(verbose_name = 'email', max_length = 128, unique = True)
	date_joined		= models.DateTimeField(verbose_name = 'date joined', auto_now_add = True)
	last_login		= models.DateTimeField(verbose_name = 'last login', auto_now = True)


	#hide_email

	# override the default behaviour since we inherit from AbstractBaseUser
	is_admin		= models.BooleanField(default=False)
	is_superuser	= models.BooleanField(default=False)
	is_staff		= models.BooleanField(default=False)
	is_active		= models.BooleanField(default=True) # - lehet false pl email-es aktivalas


	# common attributes in the game
	# roles
	#is_warrior   	= models.BooleanField(default=False)
	#is_mage 	 	= models.BooleanField(default=False)
	#is_scout 		= models.BooleanField(default=False)
	profile_image		= models.ImageField(null=True, blank=True, upload_to=profile_image_path, default=default_profile_image)


	# defining our CustomAccountManager
	objects = CustomAccountManager()


	USERNAME_FIELD 	= 'username'
	REQUIRED_FIELDS	= ['email']

	def __str__(self):
		return self.username


	def has_perm(self, perm, obj=None):
		return self.is_admin


	def has_module_perms(self, app_label):
		return True


	#save uploaded profile pic mas neven
	def get_profile_image_filename(self):
		return str(self.profile_image)[str(self.profile_image).index(f'profile_images/{self.pk}/'):],




class Character(models.Model):
	account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True) 

	ROLES = (
		('warrior', 'warrior'),
		('mage', 'mage'),
		('scout', 'scout'),
	)

	character_type	= models.CharField(verbose_name = 'character type', max_length = 20, choices=ROLES, default='')

	level			= models.DecimalField(verbose_name='level', max_digits=19, decimal_places=0, default = 1) #szint

	# attributes
	strength		= models.DecimalField(verbose_name='strength', max_digits=19, decimal_places=0, default = 8) #erő
	skill 			= models.DecimalField(verbose_name='skill', max_digits=19, decimal_places=0, default = 6) #ügyesség
	intelligence	= models.DecimalField(verbose_name='intelligence', max_digits=19, decimal_places=0, default = 7) #értelem
	health_point	= models.DecimalField(verbose_name='health point', max_digits=19, decimal_places=0, default = 10) #életerő
	fortune 		= models.DecimalField(verbose_name='fortune', max_digits=19, decimal_places=0, default = 8) #szerencse

	shield 			= models.DecimalField(verbose_name='shield', max_digits=19, decimal_places=0, default = 0) #páncél


	rank			= models.DecimalField(verbose_name='rank', max_digits=19, decimal_places=0, blank = True, null = True) #helyezes
	honor			= models.DecimalField(verbose_name='honor', max_digits=19, decimal_places=0, default = 1) #becsuletpont
	#team



	def __str__ (self):
		return self.account.username





class CharacterHistory(models.Model):
	account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True) 

	matches_played	= models.DecimalField(verbose_name='matches played', max_digits=19, decimal_places=0, default = 0)
	#more attributes coming soon


	def __str__ (self):
		return self.account.username


@receiver(post_save, sender=Account)
def create_account(sender, instance, created, **kwargs):

	if created: # created is True if the account is not exists yet, it's false if the account already exists

		profile 		= Character.objects.create(account=instance)
		profile_history = CharacterHistory.objects.create(account=instance)



# https://stackoverflow.com/questions/19287719/remove-previous-image-from-media-folder-when-imagefiled-entry-modified-in-django
#https://docs.djangoproject.com/en/4.0/ref/models/fields/
@receiver(pre_save, sender=Account)
def delete_old_profile_image(sender, instance, **kwargs):
	if instance.id:
		account = Account.objects.get(id=instance.id)
		if instance.profile_image and account.profile_image != instance.profile_image:
			account.profile_image.delete(False)


"""

@receiver(post_save, sender=Account)
def update_account(sender, instance, created, **kwargs):
	profile = Character.objects.get(account=instance)

	if created == False:
		profile.save()
		print('Character is updated')
"""