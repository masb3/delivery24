import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
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
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'), max_length=254)
    phone = PhoneNumberField(_('phone'), help_text=_('Contact phone number'))
    address_from = models.CharField(_('address from'), max_length=128)
    address_to = models.CharField(_('address to'), max_length=128)
    delivery_date = models.DateTimeField(_('delivery date'))
    message = models.TextField(_('message'), help_text=_('additional information'), blank=True)
    verified = models.BooleanField(default=False)
    work = models.ForeignKey(Work,
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True,
                             related_name='works',
                             related_query_name='work')

    def __str__(self):
        return self.email
