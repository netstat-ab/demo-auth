"""
Тестирование повторной регистрации, когда запрашиваемый email зарегистрирован, но не подтвержден.
"""

import freezegun
import pytest

from app.accounts.models import User, Registration
from . import constants
from ._base import UserRegistrationTestBase

pytestmark = pytest.mark.django_db


class NotConfirmedUserTestBase(UserRegistrationTestBase):
    @pytest.fixture
    def data(self, now, user, password='P@ssw0rd') -> dict:
        assert user.is_active
        assert not user.has_verified_email
        assert not user.check_password(password)
        assert user.created_at != now
        return {
            'email': user.email,
            'password': password,
            'password_confirmation': password,
        }

    @pytest.mark.django_db(transaction=True)
    def test_it_sends_registration_email(self, client, url, data, email_service, registration_code):
        client.post(url, data=data, content_type='application/json')
        assert email_service.success_emails == [(data['email'], registration_code)]

    def test_it_does_not_creates_user(self, client, url, data):
        users_count = User.objects.count()
        client.post(url, data=data, content_type='application/json')
        assert User.objects.count() == users_count

    def test_sets_does_not_modifies_created_at(self, client, url, data, now):
        user = User.objects.get(email=data['email'])
        previous_created_at_value = user.created_at
        with freezegun.freeze_time(now):
            client.post(url, data=data, content_type='application/json')
        user.refresh_from_db()
        assert user.created_at == previous_created_at_value


class TestUserHaveNoRegistrationRecord(NotConfirmedUserTestBase):
    @pytest.fixture
    def user(self):
        u = User.objects.get(email=constants.USER_1_EMAIL)
        assert not Registration.objects.filter(user=u).exists()
        return u


class TestUserHaveRegistrationRecord(NotConfirmedUserTestBase):
    @pytest.fixture
    def user(self):
        return User.objects.get(email=constants.USER_2_EMAIL)

    @pytest.fixture
    def existing_registration_id(self, user):
        registration = Registration.objects.get(user=user)
        assert registration.code == constants.USER_1_REGISTRATION_CODE
        return registration.id

    def test_it_removes_old_registration_record(self, client, url, data, existing_registration_id, now):
        client.post(url, data=data, content_type='application/json')
        assert not Registration.objects.filter(id=existing_registration_id).exists()
