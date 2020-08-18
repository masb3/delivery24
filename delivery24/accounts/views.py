from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from .forms import SignUpForm, CustomLoginForm, CustomPasswordChangeForm, CustomPasswordResetForm
from .models import User

from delivery24 import settings


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomLoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # TODO: redirect to /accounts/profile/
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(CustomLoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(CustomLoginView, self).post(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('accounts:password_reset_done')
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
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


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/changepwd.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('core:index')


def signup(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.car_number = form.cleaned_data.get('car_number').replace(' ', '').upper()
                user.save()
                current_site = get_current_site(request)
                subject = 'Activate Your delivery24.ee Account'
                message = render_to_string('accounts/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                # Below uses send_email defined in model
                # user.email_user(subject, message)

                # Below sets content type html
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(subject, message, to=[to_email])
                email.content_subtype = "html"
                email.send()
                return render(request, 'accounts/account_activation_sent.html')
        else:
            form = SignUpForm()
        return render(request, 'accounts/signup.html', {'driver_signup_form': form})
    else:
        return redirect('core:index')


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
        return redirect(reverse_lazy('core:index'))
    else:
        return render(request, 'accounts/account_activation_invalid.html')
