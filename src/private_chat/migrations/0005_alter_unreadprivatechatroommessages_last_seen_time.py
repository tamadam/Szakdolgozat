# Generated by Django 3.2.13 on 2022-08-11 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('private_chat', '0004_rename_sending_time_unreadprivatechatroommessages_last_seen_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unreadprivatechatroommessages',
            name='last_seen_time',
            field=models.DateTimeField(null=True),
        ),
    ]