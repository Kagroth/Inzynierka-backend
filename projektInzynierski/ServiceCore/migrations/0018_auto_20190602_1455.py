# Generated by Django 2.1.4 on 2019-06-02 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ServiceCore', '0017_auto_20190602_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='exercise',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ServiceCore.Exercise'),
        ),
    ]
