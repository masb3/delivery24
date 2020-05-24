from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ['created_at', 'updated_at', 'is_active', 'is_admin', 'groups',
                   'last_login', 'is_superuser', 'user_permissions']

