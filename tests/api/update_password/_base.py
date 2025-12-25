import freezegun
import pytest
from rest_framework import status

from app.models import User, Registration


class CommonUserRegistrationTestBase:
    """
    Базовый класс проверки регистрации, включающий тестирование общего поведения сценариев запроса регистрации
    """

    def test_it_returns_200(self, client, url, data):
        """Всегда возвращается ответ 200"""
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

    def test_it_returns_no_data(self, client, url, data):
        """Всегда в ответе отсутствуют данные"""
        response = client.post(url, data=data, content_type='application/json')
        assert response.data is None


class SuccessUserRegistrationTestBase(CommonUserRegistrationTestBase):
    """
    Базовый класс проверки регистрации, включающий тестирование общего поведения сценариев запроса регистрации
    с успешным исходом (исключается случай, когда почтовый адрес уже зарегистрирован)
    """

    def test_user_attributes(self, client, url, data):
        """Проверка корректности установки атрибутов, общих для всех сценариев"""
        client.post(url, data=data, content_type='application/json')
        user = User.objects.get(email=data['email'])
        assert not user.has_verified_email
        assert user.check_password(data['password'])

    @pytest.mark.django_db(transaction=True)
    def test_it_triggers_success_event(self, client, url, data, message_broker, registration_code):
        """Отправляется почтовое уведомление об успешной регистрации"""
        client.post(url, data=data, content_type='application/json')
        assert message_broker.success_registrations == [(data['email'], registration_code)]

    def test_it_creates_registration_record(self, client, url, data, registration_code, now):
        """Создается новая запись о регистрации"""
        assert not Registration.objects.filter(code=registration_code).exists()

        with freezegun.freeze_time(now):
            client.post(url, data=data, content_type='application/json')
        registration_record = Registration.objects.get(code=registration_code)
        assert registration_record.user.email == data['email']
        assert registration_record.code == registration_code
        assert registration_record.created_at == now
