# Generated by Django 2.1.4 on 2019-06-02 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ServiceCore', '0019_task_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='tasks',
            field=models.ManyToManyField(blank=True, related_name='assignedTo', to='ServiceCore.Task'),
        ),
    ]
