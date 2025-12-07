import freezegun
import pytest
from rest_framework import status

from app.accounts.models import User, Registration


class UserRegistrationTestBase:
    """
    Базовый класс проверки регистрации, включающий тестирование общего поведения сценариев регистрации
    """

    def test_it_returns_200(self, client, url, data):
        """Всегда возвращается ответ 200"""
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

    def test_it_returns_no_data(self, client, url, data):
        """Всегда в ответе отсутствуют данные"""
        response = client.post(url, data=data, content_type='application/json')
        assert response.data is None

    def test_user_attributes(self, client, url, data):
        """Проверка корректности установки атрибутов, общих для всех сценариев"""
        client.post(url, data=data, content_type='application/json')
        user = User.objects.get(email=data['email'])
        assert user.is_active
        assert not user.has_verified_email
        assert user.check_password(data['password'])

    @pytest.mark.django_db(transaction=True)
    def test_it_sends_registration_email(self, client, url, data, email_service, registration_code):
        """Отправляется почтовое уведомление об успешной регистрации"""
        client.post(url, data=data, content_type='application/json')
        assert email_service.success_emails == [(data['email'], registration_code)]

    def test_it_create_registration_record(self, client, url, data, registration_code, now):
        """Создается новая запись о регистрации"""
        assert not Registration.objects.filter(code=registration_code).exists()

        with freezegun.freeze_time(now):
            client.post(url, data=data, content_type='application/json')
        registration_record = Registration.objects.filter(code=registration_code).first()
        assert registration_record is not None
        assert registration_record.user.email == data['email']
        assert registration_record.code == registration_code
        assert registration_record.created_at == now
