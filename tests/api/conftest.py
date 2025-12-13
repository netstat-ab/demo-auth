import pytest
from rest_framework.test import APIClient

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
