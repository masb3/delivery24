from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden

from delivery24 import settings
from .accounts_fixtures import *


@pytest.mark.django_db
class TestLogin:
    def test_incorrect_password_login(self, client, create_user):
        url = reverse('accounts:login')
        email = 'newmail@mail.ee'
        password = 'TestPass2+'
        user = create_user(email=email, password=password)
        resp = client.post(url, data={'username': user.email, 'password': password + 'salt'})
        assert resp.status_code == 200

    def test_incorrect_email_login(self, client, create_user):
        url = reverse('accounts:login')
        email = 'newmail@mail.ee'
        password = 'TestPass2+'
        user = create_user(email=email, password=password)
        resp = client.post(url, data={'username': user.email + 'salt', 'password': password})
        assert resp.status_code == 200

    def test_incorrect_login_lock_account(self, client, create_user):
        url = reverse('accounts:login')
        email = 'newmail@mail.ee'
        password = 'TestPass2+'
        user = create_user(email=email, password=password)
        for _ in range(settings.AXES_FAILURE_LIMIT-1):
            resp = client.post(url, data={'username': user.email, 'password': password + 'salt'})
            assert resp.status_code == 200
        resp = client.post(url, data={'username': user.email, 'password': password + 'salt'})
        assert resp.status_code == HttpResponseForbidden.status_code

        # Test locked account template and redirection
        assert resp.content == render(resp.request, 'accounts/account_lockout.html').content

    def test_correct_login(self, client, create_user, test_password):
        url = reverse('accounts:login')
        user = create_user()
        resp = client.post(url, data={'username': user.email, 'password': test_password})

        # Test redirection after successful login
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == settings.LOGIN_REDIRECT_URL

    def test_login_get_view_redirects_logged_users(self, auto_login_user):
        client, user = auto_login_user()
        resp = client.get(reverse('accounts:login'))
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == settings.LOGIN_REDIRECT_URL

    def test_login_post_view_redirects_logged_users(self, auto_login_user, test_password):
        client, user = auto_login_user()
        resp = client.post(reverse('accounts:login'), data={'username': user.email, 'password': test_password})
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == settings.LOGIN_REDIRECT_URL
