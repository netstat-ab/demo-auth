import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.mocks.broker import MockMessageBroker
from tests.mocks.registration_code import MockRegistrationCodeGenerator
from . import constants


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture(autouse=True)
def password_min_length():
    return constants.PASSWORD_POLICY_MIN_LENGTH


@pytest.fixture(autouse=True)
def password_max_length():
    return constants.PASSWORD_POLICY_MAX_LENGTH


@pytest.fixture
def now():
    return constants.NOW


@pytest.fixture(autouse=True)
def configure_password_policy(settings, password_min_length, password_max_length):
    settings.PASSWORD_POLICY = {
        'min_length': password_min_length,
        'max_length': password_max_length,
    }


@pytest.fixture(autouse=True)
def message_broker(settings) -> type[MockMessageBroker]:
    settings.MESSAGE_BROKER_CONFIG = {'path': 'tests.mocks.broker.MockMessageBroker'}
    MockMessageBroker.cleanup()
    return MockMessageBroker


@pytest.fixture(autouse=True)
def registration_code():
    return constants.NEW_REGISTRATION_CODE


@pytest.fixture(autouse=True)
def registration_code_service(settings, registration_code):
    settings.REGISTRATION_CODE_GENERATOR_CONFIG = {
        'path': 'tests.mocks.registration_code.MockRegistrationCodeGenerator',
        'args': [registration_code]
    }
    return MockRegistrationCodeGenerator


@pytest.fixture
def url():
    return reverse('user-register')
