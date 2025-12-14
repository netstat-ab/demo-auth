__all__ = ['LoginError', 'login']

from app.models import User
from app.services import JwtToken, JwtTokenService


class LoginError(Exception):
    ...


def login(email: str, password: str) -> tuple[JwtToken, JwtToken]:
    try:
        user = User.objects.get(email=email, has_verified_email=True)
    except User.DoesNotExist:
        raise LoginError

    if not user.check_password(password):
        raise LoginError

    service = JwtTokenService.get_instance()
    return service.generate_refresh(email), service.generate_access(email, {})
