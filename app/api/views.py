__all__ = ['UserViewSet']

from django.db.transaction import atomic
from rest_framework import viewsets, decorators, status
from rest_framework.response import Response

from app import use_cases
from . import serializers
from .auth import anonymous_only, authenticated_only


# TODO:
#  refresh access token
#  refresh refresh token
#  logout (revoke access token + revoke access token)
#  update password
#  recover password
class UserViewSet(viewsets.ViewSet):
    @decorators.action(methods=['POST'], detail=False)
    @anonymous_only
    @atomic
    def register(self, request):
        data = self._get_validated_data(request.data, serializers.RegisterSerializer)
        use_cases.register_user(email=data['email'], password=data['password'])
        return Response(status=status.HTTP_200_OK)

    @decorators.action(methods=['GET'], detail=False)
    @anonymous_only
    @atomic
    def verify(self, request):
        data = self._get_validated_data(request.query_params, serializers.VerifyEmailSerializer)
        try:
            use_cases.verify_email(code=data['code'])
        except use_cases.EmailVerificationError:
            data = {'status': 'failed', 'details': {'reason': 'invalid_code'}}
        else:
            data = {'status': 'success'}
        return Response(status=status.HTTP_200_OK, data=data)

    @decorators.action(methods=['POST'], detail=False, url_path='password-update')
    @authenticated_only
    def update_password(self, request):
        ...

    @decorators.action(methods=['POST'], detail=False, url_path='password-recover')
    @anonymous_only
    def recover_password(self, request):
        ...

    @decorators.action(methods=['GET'], detail=False, url_path='password-reset')
    @anonymous_only
    def reset_password(self, request):
        ...

    @decorators.action(methods=['GET'], detail=False, url_path='profile')
    @authenticated_only
    def get_profile(self, request):
        ...

    @decorators.action(methods=['POST'], detail=False)
    @anonymous_only
    def login(self, request):
        data = self._get_validated_data(request.query_params, serializers.LoginSerializer)
        try:
            refresh_token = use_cases.login(email=data['email'], password=data['password'])
        except use_cases.LoginError:
            data = {'status': 'failed', 'details': {'reason': 'invalid_credentials'}}
        else:
            data = {'status': 'success', 'details': {'refresh_token': refresh_token}}
        return Response(status=status.HTTP_200_OK, data=data)

    @decorators.action(methods=['POST'], detail=False, url_path='create-access')
    def create_access_token(self, request):
        ...

    @decorators.action(methods=['POST'], detail=False, url_path='refresh-refresh')
    def refresh_refresh_token(self, request):
        ...

    @decorators.action(methods=['POST'], detail=False, url_path='revoke')
    def logout(self, request):
        ...

    @staticmethod
    def _get_validated_data(plain_data, serializer_class):
        serializer = serializer_class(data=plain_data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
