import uuid

from django.db import models
from django.contrib.auth.models import User
from phone_field import PhoneField


class Driver(User):
    name = models.CharField(max_length=100)


class Work(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Driver,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True,
                               related_name='drivers',
                               rel='driver')
    deliver_from = models.CharField(max_length=500)
    deliver_to = models.CharField(max_length=500)
    deliver_date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    def __str__(self):
        return f'Deliver from: {self.deliver_from}\nDeliver to: {self.deliver_to}\nDate: {self.deliver_date}'


class UserRequest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = PhoneField(help_text='Contact phone number')
    verified = models.BooleanField(default=False)
    work = models.ForeignKey(Work,
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True,
                             related_name='works',
                             rel='work')

    def __str__(self):
        return self.name
