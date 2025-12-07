__all__ = [
    'EventsService',
    'EmailServiceError',
]

import abc

from django.utils.translation import gettext_lazy as _

from app.utils import AdapterMixin


class EmailServiceError(Exception):
    ...


class EventsService(AdapterMixin, abc.ABC):
    adapter_config = 'EMAIL_SERVICE_ADAPTER'

    @abc.abstractmethod
    def send(
            self,
            subject: str,
            recipients: list[str],
            body: str,
            content_type: str = 'text/plain',
    ):
        ...

    def registration_success(self, recipient: str, registration_code: str):
        self.send(
            subject=_('Registration'),
            recipients=[recipient],
            body=f'confirm your email address {registration_code}',
        )

    def registration_warning(self, recipient: str):
        ...


class EventsServiceImpl(EventsService):
    def send(
            self,
            subject: str,
            recipients: list[str],
            body: str,
            content_type: str = 'text/plain',
    ):
        ...
