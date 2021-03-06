from django.contrib.auth import password_validation
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm)
from django.forms import TextInput, Select, PasswordInput, CharField, EmailField, EmailInput, ChoiceField, RadioSelect
from django.utils.translation import ugettext_lazy as _

import core.proj_conf as conf

from .models import User
from core.utils import set_language
from core.tasks import send_email_task


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
        fields = ('first_name', 'last_name', 'email', 'phone', 'ik', 'car_model', 'car_type',
                  'car_number', 'car_carrying', 'movers_num', 'payment', 'preferred_language',)
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'last_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'email': TextInput(attrs={'class': 'form-control rounded-0'}),
            'phone': TextInput(attrs={'class': 'form-control rounded-0'}),
            'ik': TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': ''}),
            'car_model': TextInput(attrs={'size': 50, 'class': 'form-control rounded-0'}),
            'car_type': RadioSelect(choices=conf.CAR_TYPE),
            'car_number': TextInput(attrs={'size': 7, 'class': 'form-control rounded-0'}),
            'car_carrying': TextInput(attrs={'type': 'number',
                                             'min': 100,
                                             'max': 10000,
                                             'step': 50,
                                             'class': 'form-control rounded-0'}),

            'movers_num': Select(attrs={'class': 'form-control rounded-0'}),
            'payment': Select(attrs={'class': 'form-control rounded-0'}),
            'preferred_language': Select(attrs={'class': 'form-control rounded-0'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={'class': 'form-control rounded-0'})
        self.fields['password2'].widget = PasswordInput(attrs={'class': 'form-control rounded-0'})


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = CharField(
        label=_("Old password"),
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'current-password',
                                    'autofocus': True,
                                    'class': 'form-control rounded-0'}),
    )

    new_password1 = CharField(
        label=_("New password"),
        widget=PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control rounded-0'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control rounded-0'}),
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = EmailField(
        label=_("Email"),
        max_length=254,
        widget=EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control rounded-0'})
    )

    def save(self, domain_override=None,
             subject_template_name=None,
             email_template_name=None,
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        user = User.objects.get(email=email)
        set_language(user.preferred_language)
        subject = _("Password reset")
        message = render_to_string(email_template_name, {
            'email': email,
            'domain': get_current_site(request).domain,
            'site_name': get_current_site(request).name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': email,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        })
        send_email_task.delay(subject, message, to_email=email)

    def is_valid(self):
        if super(CustomPasswordResetForm, self).is_valid():
            if not User.objects.filter(email=self.cleaned_data['email']).exists():
                self.add_error('email', _('Invalid email'))
        return super(CustomPasswordResetForm, self).is_valid()
    

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = CharField(
        label=_("New password"),
        widget=PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control rounded-0'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control rounded-0'}),
    )


class ChangeProfileForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'car_model', 'car_number', 'car_type',
                  'car_carrying', 'movers_num', 'payment', 'preferred_language',)
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'last_name': TextInput(attrs={'class': 'form-control rounded-0'}),
            'phone': TextInput(attrs={'class': 'form-control rounded-0'}),
            'car_model': TextInput(attrs={'size': 50, 'class': 'form-control rounded-0'}),
            'car_type': RadioSelect(choices=conf.CAR_TYPE),
            'car_number': TextInput(attrs={'size': 7, 'class': 'form-control rounded-0'}),
            'car_carrying': TextInput(attrs={'type': 'number',
                                             'min': 100,
                                             'max': 10000,
                                             'step': 50,
                                             'class': 'form-control rounded-0'}),

            'movers_num': Select(attrs={'class': 'form-control rounded-0'}),
            'payment': Select(attrs={'class': 'form-control rounded-0'}),
            'preferred_language': Select(attrs={'class': 'form-control rounded-0'}),
        }

    def __init__(self, *args, **kwargs):
        super(ChangeProfileForm, self).__init__(*args, **kwargs)
        self.fields.pop('password1')
        self.fields.pop('password2')
