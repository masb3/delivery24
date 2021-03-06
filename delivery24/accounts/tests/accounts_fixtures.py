import pytest

from django.http import HttpRequest

from accounts.models import User

test_password = 'abcdef123456'

user_signup_data = {
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
    'password1': test_password,
    'password2': test_password
}


@pytest.fixture
def test_password():
    return test_password


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        if 'email' not in kwargs:
            kwargs['email'] = user_signup_data['email']
        if 'password' not in kwargs:
            kwargs['password'] = test_password
        return User.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
            client.login(request=HttpRequest(), username=user.email, password=test_password)
        return client, user
    return make_auto_login
