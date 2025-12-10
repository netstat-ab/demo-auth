"""
Тестирование случая обработки существующего кода верификации.
У пользователя не установлен флаг "Верифицированный адрес электронной почты"
"""

import pytest
from rest_framework import status

from app.models import Registration
from tests.api import constants

pytestmark = pytest.mark.django_db


@pytest.fixture
def code():
    return constants.USER_2_REGISTRATION_CODE


@pytest.fixture
def query_params(code):
    return {'code': code}


@pytest.fixture
def registration(code):
    return Registration.objects.select_related('user').get(code=code)


@pytest.fixture
def user(registration):
    user = registration.user
    assert not user.has_verified_email
    return user


def test_it_responds_with_200(do_get, query_params):
    response = do_get(data=query_params)
    assert response.status_code == status.HTTP_200_OK


def test_it_responds_with_status_success(do_get, query_params):
    response = do_get(data=query_params)
    assert response.json() == {'status': 'success'}


def test_it_sets_user_has_verified_email_flag(do_get, query_params, user):
    do_get(data=query_params)
    user.refresh_from_db()
    assert user.has_verified_email


def test_it_drops_registration_record(do_get, query_params, registration):
    do_get(data=query_params)
    assert not Registration.objects.filter(pk=registration.id).exists()


@pytest.mark.django_db(transaction=True)
def test_it_triggers_email_verified_event(do_get, query_params, message_broker, user):
    do_get(data=query_params)
    assert message_broker.email_verifications == [user]
