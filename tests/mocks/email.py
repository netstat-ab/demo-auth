from app.services.email import EmailService


class MockEmailService(EmailService):
    success_emails = []
    warning_emails = []

    def send(self, subject: str, recipients: list[str], body: str, content_type='text/plain'):
        raise NotImplementedError()

    def send_registration_success(self, recipient: str, registration_code: str):
        self.success_emails.append((recipient, registration_code))

    def send_registration_warning(self, recipient: str):
        self.warning_emails.append(recipient)

    @classmethod
    def cleanup(cls):
        cls.success_emails = []
        cls.warning_emails = []
