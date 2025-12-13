__all__ = ['MessageBroker', 'MessageBrokerError']

import abc

from app.models import User
from ._base import BaseService


class MessageBrokerError(Exception):
    ...


class MessageBroker(BaseService, abc.ABC):
    settings_key = 'MESSAGE_BROKER'

    @abc.abstractmethod
    def registration_success(self, recipient: str, registration_code: str):
        ...

    @abc.abstractmethod
    def registration_warning(self, recipient: str):
        ...

    @abc.abstractmethod
    def email_verified(self, user: User):
        ...


class MessageBrokerImpl(MessageBroker):
    def registration_success(self, recipient: str, registration_code: str):
        raise NotImplementedError

    def registration_warning(self, recipient: str):
        raise NotImplementedError

    def email_verified(self, user):
        raise NotImplementedError
