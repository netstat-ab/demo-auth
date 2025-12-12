from app.services.registration_code import RegistrationCodeGenerator


class MockRegistrationCodeGenerator(RegistrationCodeGenerator):
    def do_generate(self) -> str:
        return self.config['code']
