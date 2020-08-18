from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.forms import TextInput, Select, PasswordInput, CharField
from django.utils.translation import ugettext_lazy as _
from .models import User


class CustomLoginForm(AuthenticationForm):
    username = UsernameField(label=_('User Email'),
                             widget=TextInput(attrs={'autofocus': True, 'class': 'form-control rounded-0'}))
    password = CharField(
        label=_('Password'),
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control rounded-0'}),
    )


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'ik', 'car_model',
                  'car_number', 'car_carrying', 'movers_num', 'payment')
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'last_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'email': TextInput(attrs={'class': 'form-control rounded-0'}),
            'phone': TextInput(attrs={'class': 'form-control rounded-0'}),
            'ik': TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': ''}),
            'car_model': TextInput(attrs={'size': 50, 'class': 'form-control rounded-0'}),
            'car_number': TextInput(attrs={'size': 7, 'class': 'form-control rounded-0'}),
            'car_carrying': TextInput(attrs={'type': 'number',
                                             'min': 100,
                                             'max': 10000,
                                             'step': 50,
                                             'class': 'form-control rounded-0'}),

            'movers_num': Select(attrs={'class': 'form-control rounded-0'}),
            'payment': Select(attrs={'class': 'form-control rounded-0'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={'class': 'form-control rounded-0'})
        self.fields['password2'].widget = PasswordInput(attrs={'class': 'form-control rounded-0'})
