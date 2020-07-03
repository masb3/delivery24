import datetime

from django.forms import ModelForm, Form, TextInput, Textarea, DateTimeInput, DateTimeField, CharField, Select
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Order


class DateWidget(DateTimeInput):
    input_type = 'text'


class OrderForm(ModelForm):
    DELIVERY_TIMEDELTA_MIN_H = 1  # hours
    DELIVERY_TIMEDELTA_MAX_H = 12  # hours
    DELIVERY_TIMEDELTA_START_MIN_H = 1  # hours
    DELIVERY_TIMEDELTA_START_MAX_D = 7  # days

    delivery_start = DateTimeField(input_formats=['%d/%m/%Y %H:%M'],
                                   widget=DateWidget(attrs={'class': 'form-control rounded-0'}))
    delivery_end = DateTimeField(input_formats=['%d/%m/%Y %H:%M'],
                                 widget=DateWidget(attrs={'class': 'form-control rounded-0'}))

    class Meta:
        model = Order
        exclude = ('order_id', 'verified', 'work', 'verification_code')

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'last_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'email': TextInput(attrs={'class': 'form-control rounded-0'}),
            'phone': TextInput(attrs={'class': 'form-control rounded-0'}),
            'address_from': TextInput(attrs={'class': 'form-control rounded-0'}),
            'address_to': TextInput(attrs={'class': 'form-control rounded-0'}),
            'movers_num': Select(attrs={'class': 'form-control rounded-0'}),
            'message': Textarea(attrs={'class': 'form-control rounded-0',
                                       'cols': 30, 'rows': 7,
                                       'placeholder': _("Leave your message here...")}),
        }

    def clean(self):
        cleaned_data = super().clean()
        input_delivery_start = cleaned_data.get('delivery_start')
        input_delivery_end = cleaned_data.get('delivery_end')

        tallinn_time_now = timezone.now() + datetime.timedelta(hours=3)  # Tallinn time UTC+3

        if input_delivery_start < (tallinn_time_now + datetime.timedelta(hours=self.DELIVERY_TIMEDELTA_START_MIN_H)):
            msg = _(f'Must be at least {self.DELIVERY_TIMEDELTA_START_MIN_H} hour from current time')
            self.add_error('delivery_start', msg)
        elif input_delivery_start > (tallinn_time_now + datetime.timedelta(days=self.DELIVERY_TIMEDELTA_START_MAX_D)):
            msg = _(f'Must be less than {self.DELIVERY_TIMEDELTA_START_MAX_D} days from current date')
            self.add_error('delivery_start', msg)
        elif input_delivery_end < (input_delivery_start + datetime.timedelta(hours=self.DELIVERY_TIMEDELTA_MIN_H)):
            msg = _(f'Must be at least {self.DELIVERY_TIMEDELTA_MIN_H} hour after delivery start')
            self.add_error('delivery_end', msg)
        elif input_delivery_end > (input_delivery_start + datetime.timedelta(hours=self.DELIVERY_TIMEDELTA_MAX_H)):
            msg = _(f'Must be less than {self.DELIVERY_TIMEDELTA_MAX_H} hours after delivery start')
            self.add_error('delivery_end', msg)


class OrderVeriffForm(Form):
    verification_code = CharField(
        widget=TextInput(attrs={'class': 'form-control rounded-0'})
    )

    def clean_verification_code(self):
        input_veriff_code = self.cleaned_data.get('verification_code')
        existing = Order.objects.filter(verification_code=input_veriff_code).exists()

        if not existing:
            raise ValidationError(_('Invalid code'))
        return input_veriff_code


class OrderCompleteForm(ModelForm):
    delivery_start = DateTimeField(input_formats=['%d/%m/%Y %H:%M'],
                                   widget=DateWidget(attrs={'class': 'form-control rounded-0',
                                                            'readonly': 'readonly',
                                                            'disabled': 'disabled'}))
    delivery_end = DateTimeField(input_formats=['%d/%m/%Y %H:%M'],
                                 widget=DateWidget(attrs={'class': 'form-control rounded-0',
                                                          'readonly': 'readonly',
                                                          'disabled': 'disabled'}))

    class Meta:
        model = Order
        exclude = ('order_id', 'verified', 'work', 'verification_code')

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'last_name': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'email': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'phone': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'address_from': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'address_to': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'movers_num': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'message': Textarea(attrs={'class': 'form-control rounded-0',
                                       'cols': 30, 'rows': 7,
                                       'placeholder': _("Leave your message here..."),
                                       'readonly': 'readonly'}),
        }
