# Generated by Django 3.0.6 on 2020-10-05 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20201001_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='movers_num',
            field=models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')], default=0, verbose_name='number of required movers'),
        ),
    ]