# Generated by Django 3.0.6 on 2020-06-17 23:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20200617_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='car_carrying',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(100), django.core.validators.MaxValueValidator(10000)], verbose_name='car carrying (kg)'),
        ),
    ]