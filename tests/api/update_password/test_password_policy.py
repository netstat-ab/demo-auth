"""Тестирование политик требований к сложности пароля"""

import string
from functools import partial

import pytest
from rest_framework import status

from app import constants
from tests.api.utils import authorization_header

pytestmark = pytest.mark.django_db

empty = object()

MIN_LENGTH = 8
MAX_LENGTH = 10


@pytest.fixture
def data(authenticated_user_password):
    def factory(new_password: str):
        return {
            'current_password': authenticated_user_password,
            'new_password': new_password,
            'new_password_confirmation': new_password,
        }

    return factory


@pytest.fixture(autouse=True)
def configure_jwt_token_service(jwt_token_service):
    pass


@pytest.fixture
def configure_password_policy(settings):
    def factory(min_length: int, max_length: int):
        settings.PASSWORD_POLICY = {'min_length': min_length, 'max_length': max_length}

    return factory


@pytest.fixture
def request_password_update(client, url, authenticated_user, authenticated_user_access_token):
    return partial(
        client.post,
        url,
        content_type='application/json',
        headers=authorization_header(authenticated_user_access_token),
    )


def test_min_length_policy(request_password_update, data, configure_password_policy):
    """Тестирование требования минимальной длины пароля"""

    configure_password_policy(MIN_LENGTH, MAX_LENGTH)

    password = 'Aa1!sS2@'
    assert len(password) == MIN_LENGTH
    response = request_password_update(data=data(password))
    assert response.status_code == status.HTTP_200_OK

    password = password[:-1]
    response = request_password_update(data=data(password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'new_password': [constants.PASSWORD_TOO_SHORT % MIN_LENGTH]}


def test_max_length_policy(request_password_update, data, configure_password_policy):
    """Тестирование требования максимальной длины пароля"""

    configure_password_policy(MIN_LENGTH, MAX_LENGTH)

    password = 'P@ssw0rd12'
    assert len(password) == MAX_LENGTH
    response = request_password_update(data=data(password))
    assert response.status_code == status.HTTP_200_OK

    password += '1'
    response = request_password_update(data=data(password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'new_password': [constants.PASSWORD_TOO_LONG % MAX_LENGTH]}


@pytest.mark.parametrize('disallowed_char', '`<б[{')
def test_allowed_chars_policy(request_password_update, data, configure_password_policy, disallowed_char):
    """Тестирование требования разрешенных символов в пароле"""

    all_allowed_chars = string.ascii_letters + string.digits + '.,!@#$%^&*-_=+'
    configure_password_policy(MIN_LENGTH, len(all_allowed_chars) + 10)

    response = request_password_update(data=data(all_allowed_chars))
    assert response.status_code == status.HTTP_200_OK

    password = all_allowed_chars + disallowed_char
    response = request_password_update(data=data(password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'new_password': [constants.PASSWORD_CONTAINS_PROHIBITED_CHARACTERS]}


@pytest.mark.parametrize('bad_password', ('p@s1', 'P2s1', 'P@S1', 'P@s!'))
def test_required_chars_policy(request_password_update, data, configure_password_policy, bad_password):
    """Тестирование требования неободимых символов в пароле"""

    configure_password_policy(4, MAX_LENGTH)
    response = request_password_update(data=data('P@s1'))
    assert response.status_code == status.HTTP_200_OK

    response = request_password_update(data=data(bad_password))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'new_password': [constants.PASSWORD_DOES_NOT_CONTAIN_ALL_REQUIRED_CHARACTERS]}
