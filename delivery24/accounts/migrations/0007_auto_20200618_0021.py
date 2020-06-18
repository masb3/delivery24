# Generated by Django 3.0.6 on 2020-06-18 00:21

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200617_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='car_number',
            field=models.CharField(max_length=7, validators=[core.utils.car_number_validator], verbose_name='car number'),
        ),
    ]
