import uuid

from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .services.order import gen_unique_order_id, ORDER_ID_LEN


VERIFF_CODE_LEN = 4


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
    order_id = models.SlugField(unique=True, max_length=ORDER_ID_LEN)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'), max_length=254)
    phone = PhoneNumberField(_('phone'), help_text=_('Contact phone number'))
    address_from = models.CharField(_('address from'), max_length=128)
    address_to = models.CharField(_('address to'), max_length=128)
    delivery_start = models.DateTimeField(_('delivery start date-time'))
    delivery_end = models.DateTimeField(_('delivery end date-time'))
    movers_num = models.IntegerField(_('number of required movers'),
                                     choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')],
                                     default=0)
    message = models.TextField(_('message'), help_text=_('additional information'), blank=True)
    verified = models.BooleanField(default=False)
    verification_code = models.CharField(unique=True, null=True, max_length=VERIFF_CODE_LEN,
                                         validators=[MinLengthValidator(VERIFF_CODE_LEN)])
    work = models.ForeignKey(Work,
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True,
                             related_name='works',
                             related_query_name='work')

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
