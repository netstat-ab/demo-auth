from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, decorators, serializers, response

from app.accounts.password_policies import (
    PasswordMinimumLengthPolicy,
    PasswordMaximumLengthPolicy,
    PasswordAllowedCharsPolicy,
    PasswordRequiredCharsPolicy,
    PasswordPolicyError,
)
from app.accounts.use_cases import register_user, RegistrationError


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    password_confirmation = serializers.CharField()

    def validate_password(self, value: str):
        policies = [
            PasswordMinimumLengthPolicy(value),
            PasswordMaximumLengthPolicy(value),
            PasswordAllowedCharsPolicy(value),
            PasswordRequiredCharsPolicy(value),
        ]
        errors = []
        for policy in policies:
            try:
                policy.apply()
            except PasswordPolicyError as e:
                errors.append(e.description)
        if errors:
            raise serializers.ValidationError(errors)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError(_('Passwords do not match.'))
        return attrs

# TODO: password too week

# TODO:
#  register
#  confirm_email
#  login (get access token + refresh token)
#  refresh access token
#  refresh refresh token
#  logout (revoke access token + revoke access token)
#  update password
#  recover password
class UserViewSet(viewsets.ViewSet):
    @decorators.action(
        methods=['POST'],
        detail=False,
    )
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            register_user(email=data['email'], password=data['password'])
        except RegistrationError as e:
            response_data = {'status': 'fail', 'details': e.details}
        else:
            response_data = {'status': 'ok'}
        return response.Response(response_data)
