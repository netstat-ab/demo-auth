import pytest
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from app.constants import INVALID_TOKEN, TOKEN_HAS_EXPIRED, STATUS_FAILED

pytestmark = pytest.mark.django_db


def test_invalid_token_format(request_refresh_access, jwt_token_service, invalid_refresh_token):
    response = request_refresh_access(data={'token': invalid_refresh_token})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'details': {'reason': _(INVALID_TOKEN)}, 'status': STATUS_FAILED}


def test_expired_token(request_refresh_access, jwt_token_service, expired_refresh_token):
    response = request_refresh_access(data={'token': expired_refresh_token})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'details': {'reason': _(TOKEN_HAS_EXPIRED)}, 'status': STATUS_FAILED}


def test_other_user_token(request_refresh_access, jwt_token_service, other_user_refresh_token):
    """
    В теле запроса токен, принадлежащий другому пользователю (не аутентифицированному). Вряд ли такое возможно.
    """
    response = request_refresh_access(data={'token': other_user_refresh_token})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'details': {'reason': _(INVALID_TOKEN)}, 'status': STATUS_FAILED}
