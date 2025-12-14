from functools import partial

import pytest
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from app.constants import ANONYMOUS_ONLY

pytestmark = pytest.mark.django_db

empty = object()


@pytest.fixture
def data() -> dict:
    return {'email': 'valid@email.addr', 'password': 'no_matter'}


@pytest.fixture
def request_login_authenticated(client, url, valid_token):
    return partial(
        client.post,
        url,
        content_type='application/json',
        headers={'Authorization': f'Bearer {valid_token}'}
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
    ],
    ids=[
        'no email',
        'blank email',
        'null email',
        'invalid email',
        'no password',
        'blank password',
        'null password',
    ]
)
def test_invalid_field(request_login, data, field, value, expected_error):
    """
    Есть недостающие поля или поля неправильного формата.
    """
    if value is empty:
        data.pop(field)
    else:
        data[field] = value
    response = request_login(data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {field: [expected_error]}


def test_authenticated(request_login_authenticated, data, jwt_token_service):
    response = request_login_authenticated(data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == [_(ANONYMOUS_ONLY)]
