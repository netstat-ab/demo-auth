__all__ = ['rotate_refresh_token', 'RotateRefreshTokenError']

from django.utils.translation import gettext_lazy as _

from app.constants import INVALID_TOKEN
from app.services import JwtToken, JwtTokenService, JwtTokenServiceException


class RotateRefreshTokenError(Exception):
    @property
    def description(self):
        return self.args[0]


def rotate_refresh_token(for_subject: str, refresh_token: JwtToken) -> JwtToken:
    service = JwtTokenService.get_instance()
    try:
        jti, sub = service.decode_refresh(refresh_token)
    except JwtTokenServiceException as e:
        raise RotateRefreshTokenError(e.description)
    if for_subject != sub:
        raise RotateRefreshTokenError(_(INVALID_TOKEN))
    return service.generate_refresh(sub)
