# Generated by Django 3.2.13 on 2022-08-08 12:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('public_chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnreadPublicChatRoomMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unread_messages_count', models.IntegerField(default=0)),
                ('recent_message', models.CharField(blank=True, max_length=200, null=True)),
                ('last_seen_time', models.DateTimeField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='public_chat.publicchatroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]