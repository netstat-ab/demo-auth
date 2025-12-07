__all__ = ['MessageBroker', 'MessageBrokerError']

import abc

from app.utils import AdapterMixin


class MessageBrokerError(Exception):
    ...


class MessageBroker(AdapterMixin, abc.ABC):
    adapter_config = 'MESSAGE_BROKER_CONFIG'

    @abc.abstractmethod
    def registration_success(self, recipient: str, registration_code: str):
        ...

    @abc.abstractmethod
    def registration_warning(self, recipient: str):
        ...


class MessageBrokerImpl(MessageBroker):
    def registration_success(self, recipient: str, registration_code: str):
        raise NotImplementedError

    def registration_warning(self, recipient: str):
        raise NotImplementedError
