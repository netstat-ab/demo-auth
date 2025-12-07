"""Тестирование политик требований к сложности пароля"""

import string
from functools import partial

import pytest
from rest_framework import status

from app.constants import text

pytestmark = pytest.mark.django_db

empty = object()

MIN_LENGTH = 8
MAX_LENGTH = 10


@pytest.fixture
def data():
    def factory(password: str):
        return {
            'email': 'valid_email@example.com',
            'password': password,
            'password_confirmation': password,
        }

    return factory


@pytest.fixture
def configure_password_policy(settings):
    def factory(min_length: int, max_length: int):
        settings.PASSWORD_POLICY = {'min_length': min_length, 'max_length': max_length}

    return factory


@pytest.fixture(autouse=True)
def configure_registration_service(settings):
    settings.REGISTRATION_CODE_SERVICE_ADAPTER = {
        'path': 'tests.mocks.registration_code.MockRegistrationCodeService',
        'args': ('12345',),
    }


@pytest.fixture(autouse=True)
def configure_email_service(settings):
    settings.EMAIL_SERVICE_ADAPTER = {
        'path': 'tests.mocks.email.MockEmailService',
    }


@pytest.fixture
def do_post(client, url):
    return partial(client.post, url, content_type='application/json')


def test_min_length_policy(do_post, data, configure_password_policy):
    """Тестирование требования минимальной длины пароля"""

    configure_password_policy(MIN_LENGTH, MAX_LENGTH)

    password = 'Aa1!sS2@'
    assert len(password) == MIN_LENGTH
    response = do_post(data=data(password))
    assert response.status_code == status.HTTP_200_OK

    password = password[:-1]
    response = do_post(data=data(password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'password': [text.PASSWORD_TOO_SHORT % MIN_LENGTH]}


def test_max_length_policy(do_post, data, configure_password_policy):
    """Тестирование требования максимальной длины пароля"""

    configure_password_policy(MIN_LENGTH, MAX_LENGTH)

    password = 'P@ssw0rd12'
    assert len(password) == MAX_LENGTH
    response = do_post(data=data(password))
    assert response.status_code == status.HTTP_200_OK

    password += '1'
    response = do_post(data=data(password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'password': [text.PASSWORD_TOO_LONG % MAX_LENGTH]}


@pytest.mark.parametrize('disallowed_char', '`<б[{')
def test_allowed_chars_policy(do_post, data, configure_password_policy, disallowed_char):
    """Тестирование требования разрешенных символов в пароле"""

    all_allowed_chars = string.ascii_letters + string.digits + '.,!@#$%^&*-_=+'
    configure_password_policy(MIN_LENGTH, len(all_allowed_chars) + 10)

    response = do_post(data=data(all_allowed_chars))
    assert response.status_code == status.HTTP_200_OK

    password = all_allowed_chars + disallowed_char
    response = do_post(data=data(password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'password': [text.PASSWORD_CONTAINS_PROHIBITED_CHARACTERS]}


@pytest.mark.parametrize('bad_password', ('p@s1', 'P2s1', 'P@S1', 'P@s!'))
def test_required_chars_policy(do_post, data, configure_password_policy, bad_password):
    """Тестирование требования неободимых символов в пароле"""

    configure_password_policy(4, MAX_LENGTH)
    response = do_post(data=data(password='P@s1'))
    assert response.status_code == status.HTTP_200_OK

    response = do_post(data=data(password=bad_password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'password': [text.PASSWORD_DOES_NOT_CONTAIN_ALL_REQUIRED_CHARACTERS]}
