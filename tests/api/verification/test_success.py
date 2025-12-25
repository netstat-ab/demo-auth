"""
Тестирование случая обработки существующего кода верификации.
У пользователя не установлен флаг "Верифицированный адрес электронной почты"
"""

import pytest
from rest_framework import status

from app.constants import STATUS_SUCCESS
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


def test_it_responds_with_200(request_verify_email, query_params):
    response = request_verify_email(data=query_params)
    assert response.status_code == status.HTTP_200_OK


def test_it_responds_with_status_success(request_verify_email, query_params):
    response = request_verify_email(data=query_params)
    assert response.json() == {'status': STATUS_SUCCESS}


def test_it_sets_user_has_verified_email_flag(request_verify_email, query_params, user):
    request_verify_email(data=query_params)
    user.refresh_from_db()
    assert user.has_verified_email


def test_it_drops_registration_record(request_verify_email, query_params, registration):
    request_verify_email(data=query_params)
    assert not Registration.objects.filter(pk=registration.id).exists()


@pytest.mark.django_db(transaction=True)
def test_it_triggers_email_verified_event(request_verify_email, query_params, message_broker, user):
    request_verify_email(data=query_params)
    assert message_broker.email_verifications == [user]
