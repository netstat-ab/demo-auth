from functools import partial

import pytest
from rest_framework import status

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
    if value is empty:
        data.pop(field)
    else:
        data[field] = value
    response = do_post(data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {field: [expected_error]}


def test_password_mismatch(do_post):
    response = do_post(data={
        'email': 'valid@example.com',
        'password': 'P@ssw0rd',
        'password_confirmation': 'DoN0tM@tch',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'non_field_errors': ['Passwords do not match.']}
