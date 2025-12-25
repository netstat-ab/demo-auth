import pytest

from app import constants

pytestmark = pytest.mark.django_db


@pytest.fixture
def data(verified_user, verified_user_password):
    return {
        'email': verified_user.email,
        'password': verified_user_password,
    }


def test_it_returns_200(request_login, data):
    request = request_login(data=data)
    assert request.status_code == 200


def test_it_responds_with_tokens_pair(request_login, data, jwt_token_service):
    request = request_login(data=data)
    assert request.json() == {
        'status': constants.STATUS_SUCCESS,
        'details': {
            'refresh_token': list(jwt_token_service.generated_refresh)[0],
            'access_token': list(jwt_token_service.generated_access)[0],
        },
    }
