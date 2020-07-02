from django.forms import ModelForm, Form, TextInput, Textarea, DateTimeInput, IntegerField, DateTimeField
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Order


class DateWidget(DateTimeInput):
    input_type = 'text'


class OrderForm(ModelForm):
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
            'message': Textarea(attrs={'class': 'form-control rounded-0',
                                       'cols': 30, 'rows': 7,
                                       'placeholder': _("Leave your message here...")}),
        }


class OrderVeriffForm(Form):
    verification_code = IntegerField(
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
            'message': Textarea(attrs={'class': 'form-control rounded-0',
                                       'cols': 30, 'rows': 7,
                                       'placeholder': _("Leave your message here..."),
                                       'readonly': 'readonly'}),
        }
