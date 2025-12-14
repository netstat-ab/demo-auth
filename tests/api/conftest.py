import pytest
from rest_framework.test import APIClient

from app.models import User, Registration
from tests.mocks import MockMessageBroker, MockJwtTokenService
from . import constants


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def now():
    return constants.NOW


@pytest.fixture(autouse=True)
def message_broker(settings) -> type[MockMessageBroker]:
    settings.MESSAGE_BROKER = {
        'path': 'tests.mocks.MockMessageBroker',
        'config': {},
    }
    MockMessageBroker.cleanup()
    return MockMessageBroker


@pytest.fixture
def authenticated_user():
    return User.objects.get(email=constants.USER_3_EMAIL)


@pytest.fixture
def authenticated_access_token():
    return 'no_matter'


@pytest.fixture
def invalid_refresh_token():
    return 'invalid_token'


@pytest.fixture
def jwt_token_service(settings, authenticated_user, authenticated_access_token):
    settings.JWT_TOKEN_SERVICE_CONFIG = {
        'path': 'tests.mocks.MockJwtTokenService',
        'config': {
            'access_tokens': {
                authenticated_access_token: (authenticated_user.email, {}),
            }
        }
    }
    MockJwtTokenService.cleanup()
    return MockJwtTokenService


@pytest.fixture
def not_existing_user_email():
    email = constants.NOT_EXISTING_USER_EMAIL
    assert not User.objects.filter(email=email).exists()
    return email


@pytest.fixture
def verified_user():
    user = User.objects.get(email=constants.USER_3_EMAIL)
    assert user.has_verified_email
    return user


@pytest.fixture
def verified_user_password(verified_user):
    password = constants.USER_3_PASSWORD
    assert verified_user.check_password(password)
    return password


@pytest.fixture
def not_verified_user_without_registration_record():
    user = User.objects.get(email=constants.USER_1_EMAIL)
    assert not user.has_verified_email
    assert not Registration.objects.filter(user=user).exists()
    return user


@pytest.fixture
def not_verified_user():
    user = User.objects.get(email=constants.USER_2_EMAIL)
    assert not user.has_verified_email
    return user


@pytest.fixture
def not_verified_user_password(not_verified_user):
    assert not_verified_user.check_password(constants.USER_2_PASSWORD)
    return constants.USER_2_PASSWORD
