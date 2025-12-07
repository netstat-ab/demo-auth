"""Тестирование чистой регистрации, когда запрашиваемый email уже зарегистрирован и подтвержден"""

import freezegun
import pytest

from app.accounts.models import User, Registration
from . import constants
from ._base import CommonUserRegistrationTestBase

pytestmark = pytest.mark.django_db


class TestExistingUser(CommonUserRegistrationTestBase):
    @pytest.fixture
    def user(self):
        u = User.objects.filter(email=constants.USER_3_EMAIL).first()
        assert u is not None
        assert u.has_verified_email
        assert not Registration.objects.filter(user=u).exists()
        return u

    @pytest.fixture
    def data(self, user, password='P@ssw0rd') -> dict:
        return {
            'email': user.email,
            'password': password,
            'password_confirmation': password,
        }

    def test_it_does_not_create_user(self, client, url, data):
        users_count = User.objects.count()
        client.post(url, data=data, content_type='application/json')
        assert users_count == User.objects.count()

    def test_does_not_modifies_user_attributes(self, client, url, data, now, user):
        def get_user_attrs():
            return user.email, user.has_verified_email, user.created_at, user.password, user.last_login
        user_attrs = get_user_attrs()

        with freezegun.freeze_time(now):
            client.post(url, data=data, content_type='application/json')
        assert get_user_attrs() == user_attrs

    def test_it_does_not_creates_registration_record(self, client, url, data, user):
        client.post(url, data=data, content_type='application/json')
        assert not Registration.objects.filter(user=user).exists()

    @pytest.mark.django_db(transaction=True)
    def test_it_sends_warning_email(self, client, url, data, email_service):
        """Отправляется почтовое уведомление о повторной попытке регистрации на данный адрес"""
        client.post(url, data=data, content_type='application/json')
        assert email_service.warning_emails == [(data['email'])]
