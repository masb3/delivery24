import uuid

from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


class Work(models.Model):
    WORK_STATUS = [
        (1, 'Not started'),
        (2, 'In progress'),
        (3, 'Done'),
        (4, 'Canceled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True,
                               related_name='drivers',
                               related_query_name='driver')
    deliver_from = models.CharField(max_length=500)
    deliver_to = models.CharField(max_length=500)
    deliver_date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    status = models.IntegerField(choices=WORK_STATUS)

    def __str__(self):
        return f'Deliver from: {self.deliver_from}\nDeliver to: {self.deliver_to}\nDate: {self.deliver_date}'


class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = PhoneNumberField(help_text='Contact phone number')
    verified = models.BooleanField(default=False)
    work = models.ForeignKey(Work,
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True,
                             related_name='works',
                             related_query_name='work')

    def __str__(self):
        return self.name
