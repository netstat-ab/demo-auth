__all__ = [
    'RegisterSerializer',
    'VerifyEmailSerializer',
    'LoginSerializer',
    'RefreshTokenSerializer',
    'UpdatePasswordSerializer'
]

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from app.constants import PASSWORDS_DO_NOT_MATCH
from app.models import Registration
from app.password_policies import (
    PasswordMinimumLengthPolicy,
    PasswordMaximumLengthPolicy,
    PasswordAllowedCharsPolicy,
    PasswordRequiredCharsPolicy,
    PasswordPolicyError,
)


def apply_password_policies(password: str):
    policies = [
        PasswordMinimumLengthPolicy(password),
        PasswordMaximumLengthPolicy(password),
        PasswordAllowedCharsPolicy(password),
        PasswordRequiredCharsPolicy(password),
    ]
    errors = []
    for policy in policies:
        try:
            policy.apply()
        except PasswordPolicyError as e:
            errors.append(e.description)
    if errors:
        raise serializers.ValidationError(errors)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    password_confirmation = serializers.CharField()

    def validate_password(self, value: str):
        apply_password_policies(value)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError(_(PASSWORDS_DO_NOT_MATCH))
        return attrs


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=Registration.MAX_CODE_LENGTH)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_confirmation = serializers.CharField()

    def validate_new_password(self, value: str):
        apply_password_policies(value)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['new_password'] != attrs['new_password_confirmation']:
            raise serializers.ValidationError(_(PASSWORDS_DO_NOT_MATCH))
        return attrs
