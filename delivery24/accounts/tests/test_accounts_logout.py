from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden

from delivery24 import settings
from .accounts_fixtures import *


def test_logout(auto_login_user):
    client, user = auto_login_user()

    # Verify that created user is logged in
    url_index = reverse('core:index')
    resp = client.get(url_index)
    assert f'You are logged in as: {user.email}' in str(resp.content)

    # Test logout, verify redirection to settings.LOGOUT_REDIRECT_URL
    url_logout = reverse('accounts:logout')
    resp = client.get(url_logout)
    assert resp.status_code == HttpResponseRedirect.status_code
    assert resp.url == settings.LOGOUT_REDIRECT_URL

    # Verify user is logged out
    resp = client.get(url_index)
    assert resp.status_code == 200
    assert "You are not logged in" in str(resp.content)

    # Verify not logged in user redirection to settings.LOGOUT_REDIRECT_URL on requesting /logout/
    resp = client.get(url_logout)
    assert resp.status_code == HttpResponseRedirect.status_code
    assert resp.url == settings.LOGOUT_REDIRECT_URL
