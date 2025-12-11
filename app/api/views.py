__all__ = ['UserViewSet']

from django.db.transaction import atomic
from rest_framework import viewsets, decorators, status
from rest_framework.response import Response

from app import use_cases
from . import serializers


# TODO:
#  refresh access token
#  refresh refresh token
#  logout (revoke access token + revoke access token)
#  update password
#  recover password
class UserViewSet(viewsets.ViewSet):
    @decorators.action(methods=['POST'], detail=False)
    @atomic
    def register(self, request):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = self._get_validated_data(request.data, serializers.RegisterSerializer)
        use_cases.register_user(email=data['email'], password=data['password'])
        return Response(status=status.HTTP_200_OK)

    @decorators.action(methods=['GET'], detail=False)
    @atomic
    def verify(self, request):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = self._get_validated_data(request.query_params, serializers.VerifyEmailSerializer)
        try:
            use_cases.verify_email(code=data['code'])
        except use_cases.EmailVerificationError:
            data = {'status': 'failed', 'details': {'reason': 'invalid_code'}}
        else:
            data = {'status': 'success'}
        return Response(status=status.HTTP_200_OK, data=data)

    @decorators.action(methods=['POST'], detail=False)
    def login(self, request):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = self._get_validated_data(request.query_params, serializers.LoginSerializer)
        try:
            refresh_token = use_cases.login(email=data['email'], password=data['password'])
        except use_cases.LoginError:
            data = {'status': 'failed', 'details': {'reason': 'invalid_credentials'}}
        else:
            data = {'status': 'success', 'details': {'refresh_token': refresh_token}}
        return Response(status=status.HTTP_200_OK, data=data)

    @decorators.action(methods=['POST'], detail=False, url_path='access-token')
    def get_access_token(self, request):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # TODO


    @staticmethod
    def _get_validated_data(plain_data, serializer_class):
        serializer = serializer_class(data=plain_data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
