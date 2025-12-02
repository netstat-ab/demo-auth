__all__ = [
    'register_user',
    'RegistrationError',
]

from functools import partial

from django.db import transaction

from app.accounts.models import User, Registration
from app.services.email import EmailService
from app.services.registration_code import generate_registration_code

PASSWORD_POLICY_VIOLATION = 1


def register_user(email: str, password: str) -> User:
    return RegisterUser(email, password).execute()


class RegistrationError(Exception):
    def __init__(self, error_code: int):
        self.error_code = error_code


class RegisterUser:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def execute(self) -> User:
        user, created = User.objects.get_or_create(email=self.email)

        if not user.is_active or user.has_verified_email:
            self._complete_with_warning()
        else:
            if not created:
                Registration.objects.filter(user=user).delete()
            self._complete_with_success(user)

        return user

    def _complete_with_success(self, user: User):
        user.set_password(self.password)
        user.save()

        code = generate_registration_code()

        Registration.objects.create(user=user, code=code)

        email_service: EmailService = EmailService.get_instance()
        transaction.on_commit(
            partial(email_service.send_registration_success, self.email, code),
        )

    def _complete_with_warning(self):
        email_service: EmailService = EmailService.get_instance()
        transaction.on_commit(
            partial(email_service.send_registration_warning, self.email),
        )
