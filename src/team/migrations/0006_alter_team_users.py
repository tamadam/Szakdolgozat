# Generated by Django 3.2.13 on 2022-07-19 10:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('team', '0005_alter_team_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='users',
            field=models.ManyToManyField(related_name='users', through='team.Membership', to=settings.AUTH_USER_MODEL),
        ),
    ]