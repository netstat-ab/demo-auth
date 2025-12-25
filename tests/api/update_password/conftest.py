import pytest
from django.urls import reverse

from tests.api import constants


@pytest.fixture(autouse=True)
def password_min_length():
    return constants.PASSWORD_POLICY_MIN_LENGTH


@pytest.fixture(autouse=True)
def password_max_length():
    return constants.PASSWORD_POLICY_MAX_LENGTH


@pytest.fixture(autouse=True)
def configure_password_policy(settings, password_min_length, password_max_length):
    settings.PASSWORD_POLICY = {
        'min_length': password_min_length,
        'max_length': password_max_length,
    }


@pytest.fixture
def url():
    return reverse('user-update-password')
