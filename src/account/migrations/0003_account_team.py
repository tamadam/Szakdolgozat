# Generated by Django 3.2.13 on 2022-07-18 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
        ('account', '0002_character_gold'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='user_team', to='team.team'),
        ),
    ]