from functools import partial

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from app.constants import text

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def configure_email_backend(settings):
    settings.EMAIL_SERVICE_BACKEND = 'tests.mocks.email.EmailServiceMock'


@pytest.fixture
def url():
    return reverse('user-register')


empty = object()


class TestBadRequest:
    @pytest.fixture
    def data(self) -> dict:
        return {
            'email': 'valid_email@example.com',
            'password': 'P@ssw0rd',
            'password_confirmation': 'P@ssw0rd',
        }

    @pytest.fixture
    def do_post(self, client, url):
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
    def test_invalid_field(self, do_post, data, field, value, expected_error):
        if value is empty:
            data.pop(field)
        else:
            data[field] = value
        response = do_post(data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {field: [expected_error]}

    def test_password_mismatch(self, do_post):
        response = do_post(data={
            'email': 'valid@example.com',
            'password': 'P@ssw0rd',
            'password_confirmation': 'DoN0tM@tch',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': ['Passwords do not match.']}


class TestPasswordPolicy:
    MIN_LENGTH = 8
    MAX_LENGTH = 10

    @pytest.fixture
    def data(self):
        def factory(password: str):
            return {
                'email': 'valid_email@example.com',
                'password': password,
                'password_confirmation': password,
            }
        return factory

    @pytest.fixture(autouse=True)
    def configure_password_policy(self, settings):
        settings.PASSWORD_POLICY = {'min_length': self.MIN_LENGTH, 'max_length': self.MAX_LENGTH}

    @pytest.fixture
    def do_post(self, client, url):
        return partial(client.post, url, content_type='application/json')

    def test_min_length_policy(self, do_post, data):
        password = 'P@ssw0r'
        assert len(password) == self.MIN_LENGTH - 1
        data = data(password)
        response = do_post(data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'password': [text.PASSWORD_TOO_SHORT % self.MIN_LENGTH]}

    def test_max_length_policy(self, do_post, data):
        password = 'P@ssw0rd123'
        assert len(password) == self.MAX_LENGTH + 1
        data = data(password)
        response = do_post(data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'password': [text.PASSWORD_TOO_LONG % self.MAX_LENGTH]}
