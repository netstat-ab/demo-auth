from app.models import User
from app.services.broker import MessageBroker


class MockMessageBroker(MessageBroker):
    success_registrations = []
    warning_registrations = []
    email_verifications = []

    def registration_success(self, recipient: str, registration_code: str):
        self.success_registrations.append((recipient, registration_code))

    def registration_warning(self, recipient: str):
        self.warning_registrations.append(recipient)

    def email_verified(self, user: User):
        self.email_verifications.append(user)

    @classmethod
    def cleanup(cls):
        cls.success_registrations = []
        cls.warning_registrations = []
        cls.email_verifications = []
