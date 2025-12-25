__all__ = ['refresh_access_token', 'RefreshAccessTokenError']

from django.utils.translation import gettext_lazy as _

from app.constants import INVALID_TOKEN
from app.services import JwtToken, JwtTokenService, JwtTokenServiceException


class RefreshAccessTokenError(Exception):
    @property
    def description(self):
        return self.args[0]


def refresh_access_token(for_subject: str, token: JwtToken, extra: dict) -> JwtToken:
    service = JwtTokenService.get_instance()
    try:
        jti, sub = service.decode_refresh(token)
    except JwtTokenServiceException as e:
        raise RefreshAccessTokenError(e.description)
    if for_subject != sub:
        raise RefreshAccessTokenError(_(INVALID_TOKEN))
    return service.generate_access(sub, extra)
