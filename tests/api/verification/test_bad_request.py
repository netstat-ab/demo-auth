"""Тестирование некорректных запросов, ошибки 400"""

import pytest
from rest_framework import status

from app.models import Registration

pytestmark = pytest.mark.django_db


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
