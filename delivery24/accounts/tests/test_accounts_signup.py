from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render

from delivery24 import settings
from accounts.tokens import account_activation_token
from .accounts_fixtures import *


@pytest.mark.django_db
class TestSignUp:
    url = reverse('accounts:signup')
    data = {
        'email': 'john_doe@mail.ee',
        'first_name': 'john',
        'last_name': 'doe',
        'ik': 12345,
        'phone_0': 55478,
        'phone_1': 371,
        'car_model': 'vw',
        'car_carrying': 1000,
        'car_number': '123abc',
        'payment': 1,
        'password1': 'abcdef123456',
        'password2': 'abcdef123456'
    }

    def test_empty_form(self, client):
        resp = client.post(self.url, {})
        assert resp.status_code == 200

    def test_correct_signup(self, client, mailoutbox):
        resp = client.post(self.url, self.data)
        assert resp.status_code == 200
        assert resp.content == render(resp.request, 'accounts/account_activation_sent.html').content

        # Test sent email
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        subject = 'Activate Your delivery24.ee Account'
        assert mail.subject == subject
        assert mail.to == [self.data['email']]
        assert User.objects.exists() is True

        # Test activation link
        user = User.objects.get(email=self.data['email'])
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        server_name = 'testserver'
        activation_url = f"http://{server_name}" \
                         f"{reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token})}"
        assert activation_url in mail.body

        # Test user CAN'T login until email confirmed
        resp = client.post(reverse('accounts:login'),
                           data={'username': self.data['email'], 'password': self.data['password1']})
        assert resp.status_code == 200

        # Test activation link first click
        first_resp = client.get(activation_url)
        assert first_resp.status_code == HttpResponseRedirect.status_code
        assert first_resp.url == reverse('core:index')

        # Test activation link second click
        second_resp = client.get(activation_url)
        assert second_resp.status_code == 200
        exp_resp = render(resp.request, 'accounts/account_activation_invalid.html')
        assert exp_resp.content == second_resp.content

        # Test user CAN login when email confirmed
        resp = client.post(reverse('accounts:login'),
                           data={'username': self.data['email'], 'password': self.data['password1']})
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == settings.LOGIN_REDIRECT_URL

    def test_singup_get_view_redirects_already_logged_users(self, auto_login_user):
        client, user = auto_login_user()
        resp = client.get(reverse('accounts:signup'))
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == reverse('core:index')

    def test_singup_post_view_redirects_already_logged_users(self, auto_login_user):
        client, user = auto_login_user()
        resp = client.post(reverse('accounts:signup'), data=self.data)
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == reverse('core:index')
