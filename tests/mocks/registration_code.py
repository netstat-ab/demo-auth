from app.services.registration_code import RegistrationCodeService


class MockRegistrationCodeService(RegistrationCodeService):
    def __init__(self, code):
        self.code = code

    def generate(self) -> str:
        return self.code
