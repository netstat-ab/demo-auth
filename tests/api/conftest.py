import pytest
from rest_framework.test import APIClient

from tests.mocks.broker import MockMessageBroker
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
        'path': 'tests.mocks.broker.MockMessageBroker',
        'config': {},
    }
    MockMessageBroker.cleanup()
    return MockMessageBroker
