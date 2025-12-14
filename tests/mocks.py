from app.models import User
from app.services import (
    MessageBroker,
    JwtTokenService,
    JwtTokenServiceException,
    RegistrationCodeGenerator,
)


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


class MockJwtTokenService(JwtTokenService):
    generated_access = []
    generated_refresh = []

    def decode_refresh(self, token):
        return self.__decode(token, 'refresh')

    def decode_access(self, token):
        return self.__decode(token, 'access')

    def __decode(self, token, token_type):
        value = self.__find_token(token, token_type)

        if value is None:
            raise JwtTokenServiceException(JwtTokenServiceException.ERR_INVALID)

        if isinstance(value, Exception):
            raise value

        return value

    def __find_token(self, token, token_type):
        value = self.config[f'{token_type}_tokens'].get(token)
        if value is None:
            value = getattr(self, f'generated_{token_type}').get(token)
        return value

    def generate_refresh(self, sub: str):
        jti = str(len(self.generated_refresh))
        token = f'refresh:{jti}:{sub}'
        self.generated_refresh.append(token)
        return token

    def generate_access(self, sub: str, extra: dict):
        token = f'access:{len(self.generated_access)}:{sub}'
        self.generated_access.append(token)
        return token

    @classmethod
    def cleanup(cls):
        cls.generated_access.clear()
        cls.generated_refresh.clear()


class MockRegistrationCodeGenerator(RegistrationCodeGenerator):
    def do_generate(self) -> str:
        return self.config['code']
