# Generated by Django 3.2.13 on 2022-09-14 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0015_alter_teamjoinrequest_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamjoinrequest',
            name='request_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='request date'),
        ),
    ]