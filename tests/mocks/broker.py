from app.services.broker import MessageBroker


class MockMessageBroker(MessageBroker):
    success_registrations = []
    warning_registrations = []

    def registration_success(self, recipient: str, registration_code: str):
        self.success_registrations.append((recipient, registration_code))

    def registration_warning(self, recipient: str):
        self.warning_registrations.append(recipient)

    @classmethod
    def cleanup(cls):
        cls.success_registrations = []
        cls.warning_registrations = []
