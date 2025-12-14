__all__ = ['JWTAuthentication', 'anonymous_only', 'authenticated_only']

import functools

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions

from app.constants import ANONYMOUS_ONLY, INVALID_HEADER
from app.services import JwtTokenServiceException, JwtTokenService


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
            raise exceptions.AuthenticationFailed(_(INVALID_HEADER))

        auth_header = auth_header.split()

        if len(auth_header) != 2 or auth_header[0] != self.keyword:
            return

        service = JwtTokenService.get_instance()
        try:
            decoded = service.decode_access(auth_header[1])
        except JwtTokenServiceException as e:
            raise exceptions.AuthenticationFailed(e.description)
        return None, decoded

    def authenticate_header(self, request):
        return self.keyword


def anonymous_only(fun):
    """Запрещает аутентифицированным пользователям доступ к api"""

    @functools.wraps(fun)
    def wrapper(self, request, *agrs, **kwargs):
        if request.auth is not None:
            raise exceptions.ValidationError(_(ANONYMOUS_ONLY))
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
