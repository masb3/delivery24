from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.forms import SignUpForm
from accounts.models import User
from core.utils import set_language
from accounts.tokens import account_activation_token
from core.tasks import send_email_task


def save_new_driver(request, form: SignUpForm):
    user = form.save(commit=False)
    user.is_active = False
    user.car_number = form.cleaned_data.get('car_number').replace(' ', '').upper()
    user.save()
    send_driver_activate_email(request, user)


def send_driver_activate_email(request, user: User):
    current_site = get_current_site(request)
    set_language(user.preferred_language)
    subject = _('Activate Your delivery24.ee Account')
    message = render_to_string('accounts/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = User.objects.get(id=user.pk).email
    send_email_task.delay(subject, message, to_email)

