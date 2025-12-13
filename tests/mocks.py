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
    def decode_refresh(self, token):
        return self._decode(token, 'refresh')

    def decode_access(self, token):
        return self._decode(token, 'access')

    def _decode(self, token, token_type):
        tokens = self.config[f'{token_type}_tokens']
        try:
            value = tokens[token]
        except KeyError:
            raise JwtTokenServiceException(JwtTokenServiceException.ERR_INVALID)
        if isinstance(value, Exception):
            raise value
        return value

    def generate_refresh(self, sub: str):
        tokens = self.config['refresh_tokens']
        jti = str(len(tokens))
        token = f'{jti}:{sub}'
        tokens[token] = jti, sub
        return token

    def generate_access(self, sub: str, role: str, permissions: tuple[str]):
        tokens = self.config['access_tokens']
        token = f'{sub}:{role}:{":".join(permissions)}'
        tokens[token] = sub, role, permissions
        return token


class MockRegistrationCodeGenerator(RegistrationCodeGenerator):
    def do_generate(self) -> str:
        return self.config['code']
