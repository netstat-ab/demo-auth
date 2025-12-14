"""Тестирование некорректных запросов, ошибки 400"""
from functools import partial

import pytest
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from app.constants import ANONYMOUS_ONLY
from app.models import Registration

pytestmark = pytest.mark.django_db


@pytest.fixture
def do_get_authenticated(client, url, valid_token):
    return partial(
        client.get,
        url,
        content_type='application/json',
        headers={'Authorization': f'Bearer {valid_token}'}
    )


def test_no_code(do_get):
    response = do_get()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'code': ['This field is required.']}


def test_empty_code(do_get):
    response = do_get(data={'code': ''})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'code': ['This field may not be blank.']}


def test_code_too_long(do_get):
    max_len = Registration.MAX_CODE_LENGTH
    response = do_get(data={'code': 'a' * max_len})
    assert response.status_code == status.HTTP_200_OK
    response = do_get(data={'code': 'a' * (max_len + 1)})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'code': [f'Ensure this field has no more than {max_len} characters.']}


def test_authenticated(do_get_authenticated, jwt_token_service):
    response = do_get_authenticated()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [_(ANONYMOUS_ONLY)]
