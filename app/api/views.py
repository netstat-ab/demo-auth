__all__ = ['UserViewSet']

from django.db.transaction import atomic
from rest_framework import viewsets, decorators, status
from rest_framework.response import Response

from app.use_cases import register_user, verify_email, EmailVerificationError
from .serializers import RegisterSerializer, VerifyEmailSerializer


# TODO:
#  login (get access token + refresh token)
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

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        register_user(email=data['email'], password=data['password'])

        return Response(status=status.HTTP_200_OK)

    @decorators.action(methods=['POST'], detail=False)
    @atomic
    def verify(self, request):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = VerifyEmailSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            verify_email(code=data['code'])
        except EmailVerificationError:
            data = {'status': 'failed', 'details': {'reason', 'invalid_code'}}
        else:
            data = {'status': 'success'}

        return Response(status=status.HTTP_200_OK, data=data)
