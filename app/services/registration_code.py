__all__ = ['generate_registration_code', 'RegistrationCodeGenerator']

import abc
import secrets
import string

from ._base import Injectable


def generate_registration_code() -> str:
    return RegistrationCodeGenerator.get_instance().generate()


class RegistrationCodeGenerator(Injectable, abc.ABC):
    config_key = 'REGISTRATION_CODE_GENERATOR'

    def generate(self) -> str:
        code = self.do_generate()
        assert len(code) == self.config['code_length']
        return code

    @property
    def config(self) -> dict:
        return self._get_config()['config']

    @abc.abstractmethod
    def do_generate(self) -> str:
        ...


class RegistrationCodeGeneratorImpl(RegistrationCodeGenerator):
    def do_generate(self) -> str:
        """Генерация кода с буквами и цифрами"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(self.config['code_length']))
