"""Тестирование некорректных запросов, ошибки 400"""

from functools import partial

import pytest
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from app.constants import ANONYMOUS_ONLY
from app.models import User
from tests.api import constants

pytestmark = pytest.mark.django_db

empty = object()


@pytest.fixture
def data() -> dict:
    return {
        'email': 'valid_email@example.com',
        'password': 'P@ssw0rd',
        'password_confirmation': 'P@ssw0rd',
    }


@pytest.fixture
def do_post(client, url):
    return partial(client.post, url, content_type='application/json')


@pytest.fixture
def user():
    return User.objects.get(email=constants.USER_3_EMAIL)


@pytest.fixture
def token():
    return 'no_matter'


@pytest.fixture
def jwt_token_service(settings, user, token):
    settings.JWT_TOKEN_SERVICE_CONFIG = {
        'path': 'tests.mocks.MockJwtTokenService',
        'config': {
            'access_tokens': {
                token: (user.email, 'some_role', ('some_permission',)),
            }
        }
    }


@pytest.fixture
def do_post_authenticated(client, url, token):
    return partial(
        client.post,
        url,
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}

    )


@pytest.mark.parametrize(
    'field,value,expected_error',
    [
        ('email', empty, 'This field is required.'),
        ('email', '', 'This field may not be blank.'),
        ('email', None, 'This field may not be null.'),
        ('email', 'invalid', 'Enter a valid email address.'),
        ('password', empty, 'This field is required.'),
        ('password', '', 'This field may not be blank.'),
        ('password', None, 'This field may not be null.'),
        ('password_confirmation', empty, 'This field is required.'),
        ('password_confirmation', '', 'This field may not be blank.'),
        ('password_confirmation', None, 'This field may not be null.'),
    ],
    ids=[
        'no email',
        'blank email',
        'null email',
        'invalid email',
        'no password',
        'blank password',
        'null password',
        'no password_confirmation',
        'blank password_confirmation',
        'null password_confirmation',
    ]
)
def test_invalid_field(do_post, data, field, value, expected_error):
    """
    Есть недостающие поля или поля неправильного формата.
    """
    if value is empty:
        data.pop(field)
    else:
        data[field] = value
    response = do_post(data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {field: [expected_error]}


def test_password_mismatch(do_post):
    """
    Пароль не совпадает с подтверждением пароля
    """
    response = do_post(data={
        'email': 'valid@example.com',
        'password': 'P@ssw0rd',
        'password_confirmation': 'DoN0tM@tch',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'non_field_errors': ['Passwords do not match.']}


def test_authenticated(do_post_authenticated, jwt_token_service):
    response = do_post_authenticated(data={
        'email': 'valid@example.com',
        'password': 'P@ssw0rd',
        'password_confirmation': 'P@ssw0rd',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [_(ANONYMOUS_ONLY)]
