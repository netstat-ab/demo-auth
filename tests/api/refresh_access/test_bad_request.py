import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

empty = object()


@pytest.mark.parametrize(
    'refresh_token,expected_error',
    [
        (empty, 'This field is required.'),
        ('', 'This field may not be blank.'),
        (None, 'This field may not be null.'),
    ],
    ids=['no token', 'blank token', 'null token']
)
def test_invalid_token(request_refresh_access, refresh_token, expected_error, jwt_token_service):
    """
    Есть недостающие поля или поля неправильного формата.
    """
    data = {} if refresh_token is empty else {'token': refresh_token}
    response = request_refresh_access(data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'token': [expected_error]}
