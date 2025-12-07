"""Тестирование чистой регистрации, когда запрашиваемый email не зарегистрирован в системе"""

import freezegun
import pytest
from rest_framework import status

from app.accounts.models import User, Registration

pytestmark = pytest.mark.django_db


@pytest.fixture
def data() -> dict:
    return {
        'email': 'new_user@example.com',
        'password': 'P@ssw0rd',
        'password_confirmation': 'P@ssw0rd',
    }


def test_it_returns_200(client, url, data):
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK


def test_it_returns_no_data(client, url, data):
    response = client.post(url, data=data, content_type='application/json')
    assert response.data is None


def test_it_creates_user(client, url, data):
    assert not User.objects.filter(email=data['email']).exists()
    client.post(url, data=data, content_type='application/json')
    assert User.objects.filter(email=data['email']).exists()


def test_user_attributes(client, url, data, now):
    with freezegun.freeze_time(now):
        client.post(url, data=data, content_type='application/json')
    user = User.objects.get(email=data['email'])
    assert user.is_active
    assert not user.has_verified_email
    assert user.check_password(data['password'])
    assert user.created_at == now
    assert user.last_login is None


@pytest.mark.django_db(transaction=True)
def test_it_sends_registration_email(client, url, data, email_service, registration_code):
    client.post(url, data=data, content_type='application/json')
    assert email_service.success_emails == [(data['email'], registration_code)]


def test_it_create_registration_record(client, url, data, email_service, registration_code, now):
    assert not Registration.objects.filter(code=registration_code).exists()

    with freezegun.freeze_time(now):
        client.post(url, data=data, content_type='application/json')
    registration_record = Registration.objects.filter(code=registration_code).first()
    assert registration_record is not None
    assert registration_record.user.email == data['email']
    assert registration_record.code == registration_code
    assert registration_record.created_at == now
