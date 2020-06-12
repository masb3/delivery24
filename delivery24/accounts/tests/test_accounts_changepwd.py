from django.urls import reverse, resolve
from django.http import HttpResponseRedirect
from django.contrib.auth.views import PasswordChangeView
from .accounts_fixtures import *


class TestChangePassword:
    changepwd_url = reverse('accounts:changepwd')
    success_url = reverse('core:index')

    def test_changepwd_not_logged_redirected(self, client):
        resp = client.get(self.changepwd_url)
        assert resp.status_code == HttpResponseRedirect.status_code
        assert f"{reverse('accounts:login')}?next={self.changepwd_url}" == resp.url

    def test_changepwd_logged_user_resolves_status_code(self, auto_login_user):
        client, user = auto_login_user()
        resp = client.get(self.changepwd_url)
        assert resp.status_code == 200

    def test_changepwd_resolves_view(self):
        view = resolve('/accounts/changepwd/')
        assert view.func.__name__ == PasswordChangeView.as_view().__name__

    def test_changepwd_resolves_password_change(self, auto_login_user, test_password):
        client, user = auto_login_user()
        resp = client.post(self.changepwd_url,
                           data={'old_password': test_password,
                                 'new_password1': test_password, 'new_password2': test_password})
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == self.success_url

    def test_changepwd_wrong_old_password(self, auto_login_user, test_password):
        client, user = auto_login_user()
        resp = client.post(self.changepwd_url,
                           data={'old_password': str(test_password) + 'salt',
                                 'new_password1': test_password, 'new_password2': test_password})
        assert resp.status_code == 200

    def test_changepwd_wrong_new_password1(self, auto_login_user, test_password):
        client, user = auto_login_user()
        resp = client.post(self.changepwd_url,
                           data={'old_password': test_password,
                                 'new_password1': str(test_password) + 'salt', 'new_password2': test_password})
        assert resp.status_code == 200

    def test_changepwd_wrong_new_password2(self, auto_login_user, test_password):
        client, user = auto_login_user()
        resp = client.post(self.changepwd_url,
                           data={'old_password': test_password,
                                 'new_password1': test_password, 'new_password2': str(test_password) + 'salt'})
        assert resp.status_code == 200
