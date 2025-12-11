__all__ = ['register_user']

from functools import partial

from django.db import transaction
from django.db.transaction import atomic

from app.models import User, Registration
from app.services.broker import MessageBroker
from app.services.registration_code import generate_registration_code


def register_user(email: str, password: str) -> User:
    return RegisterUser(email, password).execute()


class RegisterUser:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def execute(self) -> User:
        with atomic():
            user, created = User.objects.get_or_create(email=self.email)

            if user.has_verified_email:
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

        message_broker: MessageBroker = MessageBroker.get_instance()
        transaction.on_commit(
            partial(message_broker.registration_success, self.email, code),
        )

    def _complete_with_warning(self):
        message_broker: MessageBroker = MessageBroker.get_instance()
        transaction.on_commit(
            partial(message_broker.registration_warning, self.email),
        )
