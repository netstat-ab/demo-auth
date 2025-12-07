from app.services.event import EventsService


class MockEventsService(EventsService):
    success_emails = []
    warning_emails = []

    def send(self, subject: str, recipients: list[str], body: str, content_type='text/plain'):
        raise NotImplementedError()

    def registration_success(self, recipient: str, registration_code: str):
        self.success_emails.append((recipient, registration_code))

    def registration_warning(self, recipient: str):
        self.warning_emails.append(recipient)

    @classmethod
    def cleanup(cls):
        cls.success_emails = []
        cls.warning_emails = []
