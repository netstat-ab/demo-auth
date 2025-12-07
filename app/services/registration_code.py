__all__ = ['generate_registration_code', 'RegistrationCodeGenerator']

import abc
import secrets
import string

from django.conf import settings

from app.utils import AdapterMixin


def generate_registration_code() -> str:
    return RegistrationCodeGenerator.get_instance().generate()


class RegistrationCodeGenerator(AdapterMixin, abc.ABC):
    adapter_config = 'REGISTRATION_CODE_GENERATOR_CONFIG'

    @abc.abstractmethod
    def generate(self) -> str:
        ...


class RegistrationCodeGeneratorImpl(RegistrationCodeGenerator):
    def generate(self) -> str:
        """Генерация кода с буквами и цифрами"""
        config = getattr(settings, self.adapter_config)
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in config['code_length'])
