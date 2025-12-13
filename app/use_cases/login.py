__all__ = ['LoginError', 'login']

from app.models import User
from app.services import JwtToken, generate_refresh_token


class LoginError(Exception):
    ...


def login(email: str, password: str) -> JwtToken:
    try:
        user = User.objects.get(email=email, has_verified=True)
    except User.DoesNotExist:
        raise LoginError

    if not user.check_password(password):
        raise LoginError

    return generate_refresh_token(email)
