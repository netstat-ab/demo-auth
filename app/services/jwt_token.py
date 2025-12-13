__all__ = [
    'generate_access_token',
    'generate_refresh_token',
    'decode_access_token',
    'JwtToken',
    'JwtTokenServiceException',
    'JwtTokenService',
]

import abc
import datetime
import uuid
from typing import Literal, TypeAlias

import jwt
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ._base import BaseService

JwtToken: TypeAlias = str


def generate_access_token(sub: str, role: str, permissions: tuple[str]) -> JwtToken:
    return JwtTokenService.get_instance().generate_access(sub, role, permissions)


def generate_refresh_token(sub: str) -> JwtToken:
    return JwtTokenService.get_instance().generate_refresh(sub)


def decode_access_token(token: JwtToken) -> tuple[str, str, tuple[str]]:
    return JwtTokenService.get_instance().decode_access(token)


class JwtTokenServiceException(Exception):
    ERR_INVALID = 1
    ERR_EXPIRED = 2

    DESCRIPTIONS = {
        ERR_INVALID: _('Invalid token.'),
        ERR_EXPIRED: _('Token has expired.'),
    }

    @property
    def code(self) -> int:
        return self.args[0]

    @property
    def description(self):
        return


class JwtTokenService(BaseService, abc.ABC):
    settings_key = 'JWT_TOKEN_SERVICE_CONFIG'

    @abc.abstractmethod
    def generate_access(self, sub: str, role: str, permissions: tuple[str]) -> JwtToken:
        """Генерация access токена"""

    @abc.abstractmethod
    def generate_refresh(self, sub: str) -> JwtToken:
        """Генерация refresh токена"""

    @abc.abstractmethod
    def decode_access(self, token: JwtToken) -> tuple[str, str, tuple[str]]:
        """
        Проверка и декодирование access токена
        :param token: access токен
        :returns: sub, role, permissions
        """

    @abc.abstractmethod
    def decode_refresh(self, token: JwtToken) -> tuple[str, str]:
        """
        Проверка и декодирование refresh токена
        :param token: refresh токен
        :returns: jti, sub
        """


class JwtTokenServiceImpl(JwtTokenService):
    @property
    def access_secret(self) -> str:
        return self.config['access_secret']

    @property
    def access_expires(self) -> datetime.timedelta:
        return datetime.timedelta(minutes=self.config['access_expires_minutes'])

    @property
    def refresh_secret(self) -> str:
        return self.config['refresh_secret']

    @property
    def refresh_expires(self) -> datetime.timedelta:
        return datetime.timedelta(minutes=self.config['refresh_expires_minutes'])

    @property
    def algorithm(self) -> str:
        return self.config['algorithm']

    def generate_access(self, sub, role, permissions) -> str:
        payload = {
            'type': 'access',
            'exp': self._now + self.access_expires,
            'iat': self._now,
            'sub': sub,
            'role': role,
            'permissions': permissions,
        }
        return jwt.encode(payload, self.access_secret, algorithm=self.algorithm)

    def generate_refresh(self, sub) -> str:
        refresh_payload = {
            'type': 'refresh',
            'exp': self._now + self.refresh_expires,
            'iat': self._now,
            'jti': str(uuid.uuid4()),
            'sub': sub,
        }

        return jwt.encode(refresh_payload, self.refresh_secret, algorithm=self.algorithm)

    def decode_access(self, token):
        payload = self._decode_token(token, 'access')
        return payload['sub'], payload['role'], payload['permissions']

    def decode_refresh(self, token: str):
        payload = self._decode_token(token, 'refresh')
        return payload['jti'], payload['sub']

    def _decode_token(self, token: str, token_type: Literal['access', 'refresh']) -> dict:
        secret = getattr(self, f'{token_type}_secret')

        try:
            payload = jwt.decode(token, secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise JwtTokenServiceException(JwtTokenServiceException.ERR_EXPIRED)
        except jwt.InvalidTokenError:
            raise JwtTokenServiceException(JwtTokenServiceException.ERR_INVALID)

        if payload.get('type') != token_type:
            raise JwtTokenServiceException(JwtTokenServiceException.ERR_INVALID)

        return payload

    @property
    def _now(self):
        key = '_now_value'
        if not hasattr(self, key):
            setattr(self, key, timezone.now())
        return getattr(self, key)
