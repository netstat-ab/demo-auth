import pytest
from rest_framework.test import APIClient

from app.models import User
from tests.mocks import MockMessageBroker
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
def token():
    return 'no_matter'


@pytest.fixture
def jwt_token_service(settings, authenticated_user, token):
    settings.JWT_TOKEN_SERVICE_CONFIG = {
        'path': 'tests.mocks.MockJwtTokenService',
        'config': {
            'access_tokens': {
                token: (authenticated_user.email, 'some_role', ('some_permission',)),
            }
        }
    }
