__all__ = [
    'PasswordMinimumLengthPolicy',
    'PasswordMaximumLengthPolicy',
    'PasswordAllowedCharsPolicy',
    'PasswordRequiredCharsPolicy',
    'PasswordPolicyError',
]

import abc
import re
from app.constants import text

from django.conf import settings

class PasswordPolicyError(Exception):
    @property
    def description(self) -> int:
        return self.args[0]


class PasswordPolicy(abc.ABC):
    error_description: int

    def __init__(self, password: str):
        self.password = password

    def apply(self) -> None:
        if not self._password_is_valid():
            raise PasswordPolicyError(self.error_description)

    @abc.abstractmethod
    def _password_is_valid(self) -> bool:
        ...


class PasswordMinimumLengthPolicy(PasswordPolicy):
    @property
    def error_description(self):
        return text.PASSWORD_TOO_SHORT % settings.PASSWORD_POLICY['min_length']

    def _password_is_valid(self) -> bool:
        return len(self.password) >= settings.PASSWORD_POLICY['min_length']


class PasswordMaximumLengthPolicy(PasswordPolicy):
    @property
    def error_description(self):
        return text.PASSWORD_TOO_LONG % settings.PASSWORD_POLICY['max_length']

    def _password_is_valid(self) -> bool:
        return len(self.password) <= settings.PASSWORD_POLICY['max_length']


class PasswordAllowedCharsPolicy(PasswordPolicy):
    error_description = text.PASSWORD_CONTAINS_PROHIBITED_CHARACTERS
    chars_regex = re.compile(r'^[a-zA-Z0-9.,!@#$%^&*\-_=+]*$')

    def _password_is_valid(self) -> bool:
        return self.chars_regex.match(self.password) is not None


class PasswordRequiredCharsPolicy(PasswordPolicy):
    error_description = text.PASSWORD_DOES_NOT_CONTAIN_ALL_REQUIRED_CHARACTERS

    def _password_is_valid(self) -> bool:
        return (
                self._has_lower_case()
                and self._has_upper_case()
                and self._has_digit()
                and self._has_special()
        )

    def _has_lower_case(self) -> bool:
        return any(ord('a') <= ord(char) <= ord('z') for char in self.password)

    def _has_upper_case(self) -> bool:
        return any(ord('A') <= ord(char) <= ord('Z') for char in self.password)

    def _has_digit(self) -> bool:
        return any(ord('0') <= ord(char) <= ord('9') for char in self.password)

    def _has_special(self) -> bool:
        return any(char in '.,!@#$%^&*-_=+' for char in self.password)
