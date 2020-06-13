import pytest

from django.urls import reverse, resolve
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect

from accounts.views import signup, CustomLoginView


class TestViews:
    # Test /accounts/login/
    def test_login_view_status_code(self, client):
        url = reverse('accounts:login')
        response = client.get(url)
        assert response.status_code is 200

    def test_login_url_resolves_login_view(self):
        view = resolve('/accounts/login/')
        assert view.func.__name__ == CustomLoginView.as_view().__name__

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

