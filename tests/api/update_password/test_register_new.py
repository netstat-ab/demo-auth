"""Тестирование чистой регистрации, когда запрашиваемый email не зарегистрирован в системе"""

import freezegun
import pytest

from app.models import User
from ._base import SuccessUserRegistrationTestBase

pytestmark = pytest.mark.django_db


class TestNotExistingUser(SuccessUserRegistrationTestBase):
    @pytest.fixture
    def data(self, not_existing_user_email, password='P@ssw0rd') -> dict:
        return {
            'email': not_existing_user_email,
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
