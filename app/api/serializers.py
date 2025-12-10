__all__ = ['RegisterSerializer', 'VerifyEmailSerializer']

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from app.models import Registration
from app.password_policies import (
    PasswordMinimumLengthPolicy,
    PasswordMaximumLengthPolicy,
    PasswordAllowedCharsPolicy,
    PasswordRequiredCharsPolicy,
    PasswordPolicyError,
)


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

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError(_('Passwords do not match.'))
        return attrs


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=Registration.MAX_CODE_LENGTH)
