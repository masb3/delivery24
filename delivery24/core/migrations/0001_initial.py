# Generated by Django 3.0.6 on 2020-05-24 21:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phone_field.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('deliver_from', models.CharField(max_length=500)),
                ('deliver_to', models.CharField(max_length=500)),
                ('deliver_date', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('price', models.FloatField()),
                ('status', models.IntegerField(choices=[(1, 'Not started'), (2, 'In progress'), (3, 'Done'), (4, 'Canceled')])),
                ('driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='drivers', related_query_name='driver', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', phone_field.models.PhoneField(help_text='Contact phone number', max_length=31)),
                ('verified', models.BooleanField(default=False)),
                ('work', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='works', related_query_name='work', to='core.Work')),
            ],
        ),
    ]
