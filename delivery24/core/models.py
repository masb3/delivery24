import uuid
import secrets
import string

from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

import core.proj_conf as conf


def gen_unique_order_id():
    return ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                   for _ in range(conf.ORDER_ID_LEN))


class Order(models.Model):
    order_id = models.SlugField(unique=True, max_length=conf.ORDER_ID_LEN)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'), max_length=254)
    phone = PhoneNumberField(_('phone'))
    address_from = models.CharField(_('address from'), max_length=128, help_text=_('Delivery start address'))
    address_to = models.CharField(_('address to'), max_length=128, help_text=_('Delivery end address'))
    delivery_start = models.DateTimeField(_('delivery start'), help_text=_('Delivery start time'))
    delivery_end = models.DateTimeField(_('delivery end'), help_text=_('Delivery end time'))
    movers_num = models.IntegerField(_('number of required movers'),
                                     choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')],
                                     default=0)
    car_type = models.IntegerField(_('car type'), choices=conf.CAR_TYPE, default=3)
    message = models.TextField(_('message'), help_text=_('additional information'), blank=True)
    payment = models.IntegerField(_('payment method'), choices=conf.PAYMENT_METHOD, default=conf.PAYMENT_METHOD_BOTH)
    verified = models.BooleanField(default=False)
    verification_code = models.CharField(_('Verification code'), unique=True, null=True, max_length=conf.VERIFF_CODE_LEN,
                                         validators=[MinLengthValidator(conf.VERIFF_CODE_LEN)])
    verification_code_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    drivers_notified = models.BooleanField(default=False)
    no_free_drivers = models.BooleanField(default=False)
    collecting_works = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.order_id:  # new object creating
            unique_id = gen_unique_order_id()
            is_exists = Order.objects.filter(order_id=unique_id).exists()
            while is_exists:
                unique_id = gen_unique_order_id()
                is_exists = Order.objects.filter(order_id=unique_id).exists()
            self.order_id = unique_id
        super(Order, self).save()

    def __str__(self):
        return self.email


class Work(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True,)
    deliver_from = models.CharField(max_length=500)
    deliver_to = models.CharField(max_length=500)
    delivery_start = models.DateTimeField()
    delivery_end = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    status = models.IntegerField(choices=conf.WORK_STATUS)
    order_confirmed = models.BooleanField(default=False)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Deliver from: {self.deliver_from}\nDeliver to: {self.deliver_to}\n' \
               f'Date start: {self.delivery_start}\nDate end: {self.delivery_end}\nDriver: {self.driver}'
