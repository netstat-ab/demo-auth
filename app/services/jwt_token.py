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
Sub: TypeAlias = str
Jti: TypeAlias = str
Extra: TypeAlias = dict


def generate_access_token(sub: Sub, extra: Extra) -> JwtToken:
    return JwtTokenService.get_instance().generate_access(sub, extra)


def generate_refresh_token(sub: Sub) -> JwtToken:
    return JwtTokenService.get_instance().generate_refresh(sub)


def decode_access_token(token: JwtToken) -> tuple[Sub, Extra]:
    return JwtTokenService.get_instance().decode_access(token)


def decode_refresh_token(token: JwtToken) -> tuple[Jti, Sub]:
    return JwtTokenService.get_instance().decode_refresh(token)


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
    def generate_access(self, sub: Sub, extra: Extra) -> JwtToken:
        """Генерация access токена"""

    @abc.abstractmethod
    def generate_refresh(self, sub: Sub) -> JwtToken:
        """Генерация refresh токена"""

    @abc.abstractmethod
    def decode_access(self, token: JwtToken) -> tuple[Sub, Extra]:
        """Проверка и декодирование access токена"""

    @abc.abstractmethod
    def decode_refresh(self, token: JwtToken) -> tuple[Jti, Sub]:
        """Проверка и декодирование refresh токена"""


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

    def generate_access(self, sub: Sub, extra: Extra) -> JwtToken:
        payload = {
            'type': 'access',
            'exp': self._now + self.access_expires,
            'iat': self._now,
            'sub': sub,
            'extra': extra,
        }
        return jwt.encode(payload, self.access_secret, algorithm=self.algorithm)

    def generate_refresh(self, sub: Sub) -> JwtToken:
        refresh_payload = {
            'type': 'refresh',
            'exp': self._now + self.refresh_expires,
            'iat': self._now,
            'jti': str(uuid.uuid4()),
            'sub': sub,
        }

        return jwt.encode(refresh_payload, self.refresh_secret, algorithm=self.algorithm)

    def decode_access(self, token: JwtToken) -> tuple[Sub, Extra]:
        payload = self._decode_token(token, 'access')
        return payload['sub'], payload['extra']

    def decode_refresh(self, token: JwtToken) -> tuple[Jti, Sub]:
        payload = self._decode_token(token, 'refresh')
        return payload['jti'], payload['sub']

    def _decode_token(self, token: JwtToken, token_type: Literal['access', 'refresh']) -> dict:
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
