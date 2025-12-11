__all__ = [
    'generate_access_token',
    'generate_refresh_token',
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

from app.utils import AdapterMixin

JwtToken: TypeAlias = str


def generate_access_token(sub: str, role: str, permissions: tuple[str]) -> JwtToken:
    return JwtTokenService.get_instance().generate_access(sub, role, permissions)


def generate_refresh_token(sub: str) -> JwtToken:
    return JwtTokenService.get_instance().generate_refresh(sub)


class JwtTokenServiceException(Exception):
    ERR_INVALID = 1
    ERR_EXPIRED = 2

    @property
    def code(self) -> int:
        return self.args[0]


class JwtTokenService(AdapterMixin, abc.ABC):
    adapter_config = 'JWT_TOKEN_SERVICE_CONFIG'

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
    def __init__(
            self,
            access_secret_key: str,
            access_expires: datetime.timedelta,
            refresh_secret_key: str,
            refresh_expires: datetime.timedelta,
            algorithm: str = 'HS256',
    ):
        self.access_secret = access_secret_key
        self.refresh_secret = refresh_secret_key
        self.access_expires = access_expires
        self.refresh_expires = refresh_expires
        self.algorithm = algorithm

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
