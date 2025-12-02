__all__ = [
    'EmailService',
    'EmailServiceError',
]

import abc

from django.utils.translation import gettext_lazy as _

from app.utils import AdapterMixin


class EmailServiceError(Exception):
    ...


class EmailService(AdapterMixin, abc.ABC):
    @abc.abstractmethod
    def send(
            self,
            subject: str,
            recipients: list[str],
            body: str,
            content_type: str = 'text/plain',
    ):
        ...

    def send_registration_success(self, recipient: str, registration_code: str):
        self.send(
            subject=_('Registration'),
            recipients=[recipient],
            body=f'confirm your email address {registration_code}',
        )

    def send_registration_warning(self, recipient: str):
        ...


class KafkaEmail(EmailService):
    def send(
            self,
            subject: str,
            recipients: list[str],
            body: str,
            content_type: str = 'text/plain',
    ):
        ...
