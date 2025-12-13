import pytest
from django.urls import reverse

from tests.api import constants
from tests.mocks import MockRegistrationCodeGenerator


@pytest.fixture(autouse=True)
def password_min_length():
    return constants.PASSWORD_POLICY_MIN_LENGTH


@pytest.fixture(autouse=True)
def password_max_length():
    return constants.PASSWORD_POLICY_MAX_LENGTH


@pytest.fixture(autouse=True)
def registration_code_length():
    return constants.REGISTRATION_CODE_LENGTH


@pytest.fixture(autouse=True)
def configure_password_policy(settings, password_min_length, password_max_length):
    settings.PASSWORD_POLICY = {
        'min_length': password_min_length,
        'max_length': password_max_length,
    }


@pytest.fixture(autouse=True)
def registration_code():
    return constants.NEW_REGISTRATION_CODE


@pytest.fixture(autouse=True)
def registration_code_service(settings, registration_code):
    settings.REGISTRATION_CODE_GENERATOR = {
        'path': 'tests.mocks.MockRegistrationCodeGenerator',
        'config': {
            'code': registration_code,
            'code_length': len(registration_code),
        }
    }
    return MockRegistrationCodeGenerator


@pytest.fixture
def url():
    return reverse('user-register')
