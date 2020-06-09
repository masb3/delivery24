import pytest
import pytest_django

from django.urls import reverse, resolve
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.http import HttpResponseRedirect
from django.test import TestCase

from accounts.views import signup
from accounts.models import User


class TestViews:
    # Test /accounts/login/
    def test_login_view_status_code(self, client):
        url = reverse('accounts:login')
        response = client.get(url)
        assert response.status_code is 200

    def test_login_url_resolves_login_view(self):
        view = resolve('/accounts/login/')
        assert view.func.__name__ == LoginView.as_view().__name__

    # Test /accounts/signup/
    def test_signup_view_status_code(self, client):
        url = reverse('accounts:signup')
        response = client.get(url)
        assert response.status_code is 200

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/accounts/signup/')
        assert view.func.__name__ == signup.__name__

    # Test /accounts/logout/
    @pytest.mark.django_db
    def test_logout_view_status_code(self, client):
        url = reverse('accounts:logout')
        response = client.get(url)
        assert response.status_code is HttpResponseRedirect.status_code

    @pytest.mark.django_db
    def test_logout_redirects_to_index(self, client):
        url = reverse('accounts:logout')
        response = client.get(url)
        assert response.url == reverse('core:index')

    def test_logout_url_resolves_logout_view(self):
        view = resolve('/accounts/logout/')
        assert view.func.__name__ == LogoutView.as_view().__name__


@pytest.mark.django_db
class TestSignUp:
    url = reverse('accounts:signup')
    data = {
        'email': 'john@mail.ee',
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
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == reverse('accounts:account_activation_sent')
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        subject = 'Activate Your delivery24.ee Account'
        assert mail.subject == subject
        assert mail.to == [self.data['email']]
