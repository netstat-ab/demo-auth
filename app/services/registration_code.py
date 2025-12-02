__all__ = ['generate_registration_code', 'RegistrationCodeService']

import abc
import secrets
import string

from django.conf import settings

from app.utils import AdapterMixin


def generate_registration_code() -> str:
    return RegistrationCodeService.get_instance().generate()


class RegistrationCodeService(AdapterMixin, abc.ABC):
    adapter_config = 'REGISTRATION_CODE_SERVICE_ADAPTER'

    @abc.abstractmethod
    def generate(self) -> str:
        ...


class SecureRegistrationCodeServiceAdapter(RegistrationCodeService):
    def generate(self) -> str:
        """Генерация кода с буквами и цифрами"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(settings.REGISTRATION_CODE_LENGTH))
