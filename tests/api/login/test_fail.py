import pytest
from django.utils.translation import gettext_lazy as _

from app import constants

pytestmark = pytest.mark.django_db


class LoginFailedTestBase:
    def test_it_returns_200(self, request_login, data):
        request = request_login(data=data)
        assert request.status_code == 200

    def test_response_message_is_invalid_credentials(self, request_login, data):
        request = request_login(data=data)
        assert request.json() == {
            'status': constants.STATUS_FAILED,
            'details': {'reason': _(constants.INVALID_CREDENTIALS)},
        }


class TestUserDoesNotExist(LoginFailedTestBase):
    @pytest.fixture
    def data(self, not_existing_user_email):
        return {
            'email': not_existing_user_email,
            'password': 'no_matter',
        }


class TestUserHasNoVerifiedEmail(LoginFailedTestBase):
    @pytest.fixture
    def data(self, not_verified_user, not_verified_user_password):
        return {
            'email': not_verified_user.email,
            'password': not_verified_user_password,
        }


class TestInvalidCredentials(LoginFailedTestBase):
    @pytest.fixture
    def data(self, verified_user):
        invalid_password = 'no_matter'
        assert not verified_user.check_password(invalid_password)
        return {
            'email': verified_user.email,
            'password': invalid_password,
        }
