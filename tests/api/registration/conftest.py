from datetime import datetime

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.mocks.email import MockEmailService
from tests.mocks.registration_code import MockRegistrationCodeService


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture(autouse=True)
def password_min_length():
    return 8


@pytest.fixture(autouse=True)
def password_max_length():
    return 10


@pytest.fixture
def now():
    return datetime.fromisoformat('2025-01-23T12:34:56.789012+03:00')


@pytest.fixture(autouse=True)
def configure_password_policy(settings, password_min_length, password_max_length):
    settings.PASSWORD_POLICY = {
        'min_length': password_min_length,
        'max_length': password_max_length,
    }


@pytest.fixture(autouse=True)
def email_service(settings) -> type[MockEmailService]:
    settings.EMAIL_SERVICE_ADAPTER = {'path': 'tests.mocks.email.MockEmailService'}
    MockEmailService.cleanup()
    return MockEmailService


@pytest.fixture(autouse=True)
def registration_code():
    return '1234567890'


@pytest.fixture(autouse=True)
def registration_code_service(settings, registration_code):
    settings.REGISTRATION_CODE_SERVICE_ADAPTER = {
        'path': 'tests.mocks.registration_code.MockRegistrationCodeService',
        'args': [registration_code]
    }
    return MockRegistrationCodeService


@pytest.fixture
def url():
    return reverse('user-register')
