__all__ = ['update_password', 'UpdatePasswordError']

from django.utils.translation import gettext_lazy as _

from app import constants
from app.models import User


class UpdatePasswordError(Exception):
    INVALID_PASSWORD = 1

    _error_messages = {
        INVALID_PASSWORD: _(constants.INVALID_PASSWORD),
    }

    @property
    def code(self):
        return self.args[0]

    @property
    def message(self):
        return self._error_messages[self.code]


def update_password(user_email: str, current_password: str, new_password: str):
    user = User.objects.get(email=user_email)  # User.DoesNotExist case is server error

    if not user.check_password(current_password):
        raise UpdatePasswordError(UpdatePasswordError.INVALID_PASSWORD)

    user.set_password(new_password)
    user.save()
