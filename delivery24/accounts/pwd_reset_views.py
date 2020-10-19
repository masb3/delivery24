from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

from delivery24 import settings


class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('accounts:password_reset_done')
    template_name = 'accounts/pwd_reset/password_reset_form.html'
    email_template_name = 'accounts/pwd_reset/password_reset_email.html'
    subject_template_name = None
    form_class = CustomPasswordResetForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(CustomPasswordResetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(CustomPasswordResetView, self).post(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/pwd_reset/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')
