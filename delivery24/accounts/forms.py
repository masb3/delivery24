from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.forms import TextInput
from .models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'ik', 'phone', 'car_model',
                  'car_carrying', 'car_number', 'payment',)
        widgets = {
            'ik': TextInput(attrs={'placeholder': ''}),
        }

