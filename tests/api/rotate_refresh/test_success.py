import pytest
from rest_framework import status

from app.constants import STATUS_SUCCESS

pytestmark = pytest.mark.django_db


def test_success(request_rotate_refresh, jwt_token_service, authenticated_user_refresh_token):
    response = request_rotate_refresh(data={'token': authenticated_user_refresh_token})
    assert response.status_code == status.HTTP_200_OK
    expected_data = {
        'status': STATUS_SUCCESS,
        'details': {
            'refresh_token': list(jwt_token_service.generated_refresh)[0],
        }
    }
    assert response.json() == expected_data
