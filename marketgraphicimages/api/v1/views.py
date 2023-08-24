from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views import View
from djoser.conf import settings
from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.serializers import (
    AuthSignInSerializer,
    AuthSignUpSerializer,
    ConfirmationSerializer,
)
from core.utils import send_email_with_confirmation_code

User = get_user_model()


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=('username', 'email', 'password', 'is_author'),
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'is_author': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, default=False
            ),
        },
    ),
    responses={
        200: 'Successful signup',
        400: 'Bad request',
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def auth_signup_post(request):
    serializer = AuthSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    send_email_with_confirmation_code(request)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=(
            'username', 'email', 'password',
            'is_author', 'confirmation_code',
        ),
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'is_author': openapi.Schema(
                type=openapi.TYPE_BOOLEAN, default=False
            ),
            'confirmation_code': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        200: 'Successful activation',
        400: 'Bad request',
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def auth_confirmation(request):
    serializer = ConfirmationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    access_token = AccessToken.for_user(serializer.validated_data)
    out_put_messege = {
        "token": str(access_token),
    }
    return Response(out_put_messege, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=('email', 'password',),
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        200: 'Successful signin',
        400: 'Bad request',
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_token_post(request):
    serializer = AuthSignInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    access_token = AccessToken.for_user(serializer.validated_data)
    out_put_messege = {
        "token": str(access_token),
    }
    return Response(out_put_messege, status=status.HTTP_200_OK)


class RedirectSocial(View):

    def get(self, request, *args, **kwargs):
        code, state = str(request.GET['code']), str(request.GET['state'])
        json_obj = {'code': code, 'state': state}
        return JsonResponse(json_obj)


class UserViewSet(UserViewSet):
    """Update reset_password method logic.
    The method sends a six-digit confirmation code to the user's email.
    Added reset_password_confirm_code method. It checks the confirmation code.
    Update reset_password_confirm method. This method changes the password
    after successful confirmation of the code.
    """
    def get_permissions(self):
        if self.action == 'reset_password_confirm_code':
            self.permission_classes = (
                settings.PERMISSIONS.password_reset_confirm_code
            )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'reset_password_confirm_code':
            return settings.SERIALIZERS.password_reset_confirm_code
        return super().get_serializer_class()

    @action(['post'], detail=False)
    def reset_password_confirm_code(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            is_token_valid = serializer.validated_data.get('user_confirm_code')
            is_token_valid.is_confirmed = True
            is_token_valid.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(['post'], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        user.set_password(serializer.validated_data.get('new_password'))
        user.code_owner.all().delete()
        user.save()
        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': user}
            to = [serializer.validated_data.get('email')]
            settings.EMAIL.password_changed_confirmation(
                self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)
