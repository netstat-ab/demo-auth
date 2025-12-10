from app.services.registration_code import RegistrationCodeGenerator


class MockRegistrationCodeGenerator(RegistrationCodeGenerator):
    def __init__(self, code):
        self.code = code

    def do_generate(self) -> str:
        return self.code
