from django.core.serializers.python import Serializer
from core.constants import *

class EncodeAccountObject(Serializer):
	def get_dump_object(self, obj):
		"""
		Szerializáljuk az account objectet JSON formátumra, amelyet utána visszaküldünk a viewhoz
		"""


		try:
			profile_image = obj.profile_image.url
		except Exception as e:
			profile_image = STATIC_IMAGE_PATH_IF_DEFAULT_PIC_SET

		account_object = {
			'id': str(obj.id),
			'username': str(obj.username),
			'email': str(obj.email),
			'profile_image': str(profile_image),
		}

		return account_object