from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.urls import path, reverse_lazy
from django.core.mail import EmailMessage
from .forms import SignUpForm
from .models import User


# class SignUpView(FormView):
#     template_name = 'accounts/form.html'
#     form_class = SignUpForm
#     success_url = reverse_lazy('core:index')
#
#     # def form_valid(self, form):
#     #     # This method is called when valid form data has been POSTed.
#     #     # It should return an HttpResponse.
#     #     #form.send_email()
#     #     print('++++++++++++++++++++++++++++++++++++++++++')
#     #     return super().form_valid(form)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
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
            return redirect(reverse_lazy('accounts:account_activation_sent'))
    else:
        form = SignUpForm()
    return render(request, 'accounts/form.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect(reverse_lazy('core:index'))
    else:
        return render(request, 'accounts/account_activation_invalid.html')


def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')