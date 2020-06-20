from django.forms import ModelForm
from django.forms import TextInput
from .models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ('verified', 'work')
