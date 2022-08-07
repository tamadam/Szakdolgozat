from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime


class NotificationSerializer(Serializer):
	def get_dump_object(self, obj):
		if obj.get_content_object_type() == "UnreadPrivateChatRoomMessages":
			notification_object.update({'notification_type': obj.get_content_object_type()})
			notification_object.update({'notification_id': str(obj.id)})
			notification_object.update({'verb': obj.verb})
			notification_object.update({'sending_time': str(naturaltime(obj.sending_time))})
			notification_object.update({'timestamp': str(obj.timestamp)})
			notification_object.update({
				'actions': {
					'notification_url': str(obj.notification_url),
				},
				"from": {
					"title": str(obj.content_object.get_other_user.username),
					"image_url": str(obj.content_object.get_other_user.profile_image.url)
				}
			})

		return notification_object