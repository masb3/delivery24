import pytest
import pytest_django

from django.urls import reverse, resolve
from django.test import TestCase, Client

from core.views import IndexView


class TestIndexView:
    @pytest.mark.django_db
    def test_index_view_status_code(self, client):
        url = reverse('core:index')
        response = client.get(url)
        assert response.status_code is 200

    def test_index_url_resolves_index_view(self):
        view = resolve('/')
        assert view.func.__name__ == IndexView.as_view().__name__
