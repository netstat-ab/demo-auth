"""Тестирование некорректных запросов, ошибки 400"""

from functools import partial

import pytest

from app.models import Registration

pytestmark = pytest.mark.django_db


@pytest.fixture
def do_get(client, url):
    return partial(client.get, url, content_type='application/json')


def test_no_code(do_get):
    response = do_get()
    assert response.status_code == 400
    assert response.json() == {'code': ['This field is required.']}


def test_empty_code(do_get):
    response = do_get(data={'code': ''})
    assert response.status_code == 400
    assert response.json() == {'code': ['This field may not be blank.']}


def test_code_too_long(do_get):
    max_len = Registration.MAX_CODE_LENGTH
    response = do_get(data={'code': 'a' * max_len})
    assert response.status_code == 200
    response = do_get(data={'code': 'a' * (max_len + 1)})
    assert response.status_code == 400
    assert response.json() == {'code': [f'Ensure this field has no more than {max_len} characters.']}
