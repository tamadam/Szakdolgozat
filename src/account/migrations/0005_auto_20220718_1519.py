# Generated by Django 3.2.13 on 2022-07-18 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_team_users'),
        ('account', '0004_alter_account_team'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='team',
        ),
        migrations.AddField(
            model_name='character',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_team', to='team.team'),
        ),
    ]
