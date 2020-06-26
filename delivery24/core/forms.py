from django.forms import ModelForm, Form, TextInput, Textarea, DateTimeInput, IntegerField
from django.utils.translation import ugettext_lazy as _

from .models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ('verified', 'work', 'verification_code')

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'last_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'email': TextInput(attrs={'class': 'form-control rounded-0'}),
            'phone': TextInput(attrs={'class': 'form-control rounded-0'}),
            'address_from': TextInput(attrs={'class': 'form-control rounded-0'}),
            'address_to': TextInput(attrs={'class': 'form-control rounded-0'}),
            'delivery_date': DateTimeInput(attrs={'class': 'form-control rounded-0'}),
            'message': Textarea(attrs={'class': 'form-control rounded-0',
                                       'cols': 30, 'rows': 7,
                                       'placeholder': _("Leave your message here...")}),
        }


class OrderVeriffForm(Form):
    verification_code = IntegerField(
        widget=TextInput(attrs={'class': 'form-control rounded-0'})
    )


class OrderCompleteForm(ModelForm):
    class Meta:
        model = Order
        exclude = ('verified', 'work', 'verification_code')

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'last_name': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'email': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'phone': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'address_from': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'address_to': TextInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'delivery_date': DateTimeInput(attrs={'class': 'form-control rounded-0', 'readonly': 'readonly'}),
            'message': Textarea(attrs={'class': 'form-control rounded-0',
                                       'cols': 30, 'rows': 7,
                                       'placeholder': _("Leave your message here..."),
                                       'readonly': 'readonly'}),
        }