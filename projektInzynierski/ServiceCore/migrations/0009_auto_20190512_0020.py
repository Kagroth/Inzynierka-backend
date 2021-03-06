# Generated by Django 2.1.4 on 2019-05-11 22:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ServiceCore', '0008_solution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='tasks',
            field=models.ManyToManyField(blank=True, null=True, to='ServiceCore.Task'),
        ),
        migrations.AlterField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
