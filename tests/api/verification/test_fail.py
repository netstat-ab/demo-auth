"""
Тестирование неуспешных случаев:
1) кода верификации не существует в БД;
2) код верификации существует, но у пользователя установлен флаг "Верифицированный адрес электронной почты".
   Неожидаемый маловероятный сценарий, но должен отработать корректно.
"""

import pytest
from rest_framework import status

from app.models import Registration
from tests.api import constants

pytestmark = pytest.mark.django_db


@pytest.fixture
def query_params(code):
    return {'code': code}


class FailTestBase:
    def test_it_responds_with_200(self, do_get, query_params):
        response = do_get(data=query_params)
        assert response.status_code == status.HTTP_200_OK

    def test_it_responds_with_status_fail(self, do_get, query_params):
        response = do_get(data=query_params)
        assert response.json() == {'status': 'failed', 'details': {'reason': 'invalid_code'}}

    @pytest.mark.django_db(transaction=True)
    def test_it_does_not_trigger_email_verified_event(self, do_get, query_params, message_broker):
        do_get(data=query_params)
        assert message_broker.email_verifications == []


class TestCodeDoesNotExist(FailTestBase):
    @pytest.fixture
    def code(self):
        c = constants.NEW_REGISTRATION_CODE
        assert not Registration.objects.filter(code=c).exists()
        return c


class TestUserHasVerifiedEmail(FailTestBase):
    @pytest.fixture
    def code(self):
        c = constants.USER_4_REGISTRATION_CODE
        assert Registration.objects.filter(code=c, user__has_verified_email=True).exists()
        return c
