from django.urls import reverse, resolve
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import HttpResponseRedirect
from django.contrib.auth.views import PasswordResetDoneView
from .accounts_fixtures import *
from ..views import CustomPasswordResetView

from delivery24 import settings


class TestResetPassword:
    reset_url = reverse('accounts:password_reset')

    @pytest.mark.skip
    def test_reset_view_redirect_not_logged_in(self):
        pass
        # TODO:

    def test_reset_url_resolves_reset_view(self):
        view = resolve('/accounts/reset/')
        assert view.func.__name__ == CustomPasswordResetView.as_view().__name__

    def test_reset_view_status_code(self, client):
        resp = client.get(self.reset_url)
        assert resp.status_code == 200
        assert "Forgot password" in str(resp.content)

    @pytest.mark.skip
    def test_reset_post_unavailable_email(self, client):
        # TODO:
        pass

    def test_reset_post_valid_email(self, client, create_user):
        user = create_user()
        resp = client.post(self.reset_url, data={'email': user.email})
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == reverse('accounts:password_reset_done')
        resp = client.get(resp.url)
        assert resp.status_code == 200
        exp_resp = render(resp.request, 'accounts/password_reset_done.html')
        assert exp_resp.content == resp.content
        view = resolve('/accounts/reset/done/')
        assert view.func.__name__ == PasswordResetDoneView.as_view().__name__

    def test_reset_email_sent(self, client, create_user, mailoutbox):
        user = create_user()
        resp = client.post(self.reset_url, data={'email': user.email})
        assert resp.status_code == HttpResponseRedirect.status_code

        # Test sent email
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        subject = 'delivery24.ee password reset'
        assert mail.subject == subject
        assert mail.to == [user.email]

    def test_reset_token(self, client, create_user, mailoutbox, test_password):
        user = create_user()
        resp = client.post(self.reset_url, data={'email': user.email})
        assert resp.status_code == HttpResponseRedirect.status_code
        mail = mailoutbox[0]

        # Test activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        server_name = 'testserver'
        reset_url = f"http://{server_name}" \
                    f"{reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
        assert reset_url in mail.body

        # Test reset link first click
        first_resp = client.get(reset_url)
        assert first_resp.status_code == HttpResponseRedirect.status_code
        resp = client.post(first_resp.url, data={'new_password1': test_password, 'new_password2': test_password})
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == reverse('accounts:password_reset_complete')

        # Click redirection link
        resp = client.get(resp.url)
        exp_resp = render(resp.request, 'accounts/password_reset_complete.html')
        assert resp.status_code == 200
        assert exp_resp.content == resp.content

        # Test reset link second click
        second_resp = client.get(reset_url)
        assert second_resp.status_code == 200
        assert "The password reset link was invalid, " \
               "possibly because it has already been used." in str(second_resp.content)

    def test_reset_get_view_redirects_logged_users(self, auto_login_user):
        client, user = auto_login_user()
        resp = client.get(self.reset_url)
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == settings.LOGIN_REDIRECT_URL

    def test_reset_post_view_redirects_logged_users(self, auto_login_user):
        client, user = auto_login_user()
        resp = client.post(self.reset_url, data={'email': user.email})
        assert resp.status_code == HttpResponseRedirect.status_code
        assert resp.url == settings.LOGIN_REDIRECT_URL
