# Generated by Django 2.1.4 on 2019-06-02 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ServiceCore', '0013_auto_20190601_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='isActive',
            field=models.BooleanField(default=True),
        ),
    ]
