# Generated by Django 3.2.13 on 2022-07-18 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20220718_1559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='team',
        ),
    ]
