from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms import SignUpForm, CustomLoginForm
from .models import User
from .services.signup_utils import save_new_driver

from delivery24 import settings


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:profile')
        else:
            return super(CustomLoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(CustomLoginView, self).post(request, *args, **kwargs)


def signup(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                save_new_driver(request, form)
                return render(request, 'accounts/account_activation_sent.html',
                              {'email': form.cleaned_data.get('email')})
        else:
            form = SignUpForm()
        return render(request, 'accounts/signup.html', {'driver_signup_form': form})
    else:
        return redirect('accounts:profile')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(reverse_lazy('accounts:profile'))
    else:
        return render(request, 'accounts/account_activation_invalid.html')
