"""Тестирование чистой регистрации, когда запрашиваемый email не зарегистрирован в системе"""

import freezegun
import pytest

from app.accounts.models import User
from . import constants
from ._base import SuccessUserRegistrationTestBase

pytestmark = pytest.mark.django_db


class TestNotExistingUser(SuccessUserRegistrationTestBase):
    @pytest.fixture
    def data(self, password='P@ssw0rd') -> dict:
        assert not User.objects.filter(email=constants.NOT_EXISTING_USER_EMAIL).exists()
        return {
            'email': constants.NOT_EXISTING_USER_EMAIL,
            'password': password,
            'password_confirmation': password,
        }

    def test_it_creates_user(self, client, url, data):
        client.post(url, data=data, content_type='application/json')
        assert User.objects.filter(email=data['email']).exists()

    def test_sets_correct_timestamp(self, client, url, data, now):
        with freezegun.freeze_time(now):
            client.post(url, data=data, content_type='application/json')
        user = User.objects.get(email=data['email'])
        assert user.created_at == now
