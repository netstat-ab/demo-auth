import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

MIN_LENGTH = 8
MAX_LENGTH = 10


@pytest.fixture(autouse=True)
def configure_password_policy(settings):
    settings.PASSWORD_POLICY = {'min_length': MIN_LENGTH, 'max_length': MAX_LENGTH}


@pytest.fixture
def data() -> dict:
    return {
        'email': 'new_user@example.com',
        'password': 'P@ssw0rd',
        'password_confirmation': 'P@ssw0rd',
    }


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
def response(client, url, data):
    return client.post(url, data=data, content_type='application/json')


def test_it_returns_200(response):
    assert response.status_code == status.HTTP_200_OK


def test_it_returns_no_data(response):
    assert response.data is None
