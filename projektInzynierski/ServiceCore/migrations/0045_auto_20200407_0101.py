# Generated by Django 2.1.4 on 2020-04-06 23:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ServiceCore', '0044_auto_20200407_0059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resetpasswordhash',
            name='consumed',
        ),
        migrations.RemoveField(
            model_name='resetpasswordhash',
            name='email',
        ),
        migrations.AddField(
            model_name='resetpasswordhash',
            name='account_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resetpasswordhash',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]