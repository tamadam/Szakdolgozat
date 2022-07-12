from django.core.serializers.python import Serializer

class EncodeAccountObject(Serializer):
	def get_dump_object(self, obj):
		"""
		Szerializáljuk az account objectet JSON formátumra, amelyet utána visszaküldünk a viewhoz
		"""
		account_object = {
			'id': str(obj.id),
			'username': str(obj.username),
			'email': str(obj.email),
			'profile_image': str(obj.profile_image.url),
		}

		return account_object