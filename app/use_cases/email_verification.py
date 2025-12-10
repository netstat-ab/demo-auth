__all__ = ['verify_email', 'EmailVerificationError']

from functools import partial

from django.db import transaction
from django.db.transaction import atomic

from app.models import User, Registration
from app.services.broker import MessageBroker


class EmailVerificationError(Exception):
    ...


def verify_email(code) -> None:
    with atomic():
        qs = (
            Registration.objects
            .select_related('user')
            .filter(code=code, user__has_verified_email=False)
        )
        try:
            registration = qs.get()
        except Registration.DoesNotExist:
            raise EmailVerificationError()

        message_broker: MessageBroker = MessageBroker.get_instance()
        transaction.on_commit(
            partial(message_broker.email_verified, registration.user)
        )
        Registration.objects.filter(pk=registration.pk).delete()
