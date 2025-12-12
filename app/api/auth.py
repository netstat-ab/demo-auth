__all__ = ['JWTAuthentication', 'anonymous_only', 'authenticated_only']

import functools

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions

from services import decode_access_token, JwtTokenServiceException


class JWTAuthentication(authentication.BaseAuthentication):
    """
    JWT Bearer token authentication.
    Authorization: Bearer <jwt_token>
    """

    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request)

        if not auth_header:
            return

        try:
            auth_header = auth_header.decode('utf-8')
        except UnicodeError:
            raise exceptions.AuthenticationFailed(_('Invalid header.'))

        auth_header = auth_header.split()

        if len(auth_header) != 2 or auth_header[0] != self.keyword:
            return

        try:
            return None, decode_access_token(auth_header[1])
        except JwtTokenServiceException as e:
            raise exceptions.AuthenticationFailed(e.description)

    def authenticate_header(self, request):
        return self.keyword


def anonymous_only(fun):
    """Запрещает аутентифицированным пользователям доступ к api"""

    @functools.wraps(fun)
    def wrapper(self, request, *agrs, **kwargs):
        if request.auth is not None:
            raise exceptions.ValidationError(_('Anonymous only.'))
        return fun(self, request, *agrs, **kwargs)

    return wrapper


def authenticated_only(fun):
    """Разрешает доступ к api только аутентифицированным пользователям"""

    @functools.wraps(fun)
    def wrapper(self, request, *agrs, **kwargs):
        if request.auth is None:
            raise exceptions.NotAuthenticated()
        return fun(self, request, *agrs, **kwargs)

    return wrapper
