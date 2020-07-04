from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.forms import TextInput, Select
from .models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'ik', 'phone', 'car_model',
                  'car_carrying', 'car_number', 'payment', 'movers_num')
        widgets = {
            'ik': TextInput(attrs={'placeholder': ''}),
            'car_carrying': TextInput(attrs={'type': 'number',
                                             'min': 100,
                                             'max': 10000,
                                             'step': 50}),
            'car_number': TextInput(attrs={'size': 7}),
            'movers_num': Select(attrs={'class': 'form-control rounded-0'}),
        }
