from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils.timezone import now
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.serializers import (AuthSignInSerializer, AuthSignUpSerializer,
                                ConfirmationSerializer)
from core.utils import send_email_with_confirmation_code
from users.serializers import EmailAndTokenSerializer

User = get_user_model()


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=('username', 'email', 'password', 'is_author'),
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
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
    try:
        user, _ = User.objects.get_or_create(
            username=request.data.get('username'),
            email=request.data.get('email'),
            author=(serializer.validated_data.get('is_author')),
        )
    except IntegrityError:
        return Response(
            "Пользователь с такими данными уже существует",
            status=status.HTTP_400_BAD_REQUEST,
        )
    user.set_password(serializer.validated_data.get('password'))
    user.save()
    send_email_with_confirmation_code(request)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=('username', 'confirmation_code',),
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
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
    user = serializer.validated_data
    user.is_active = True
    user.save()
    access_token = AccessToken.for_user(user)
    out_put_messege = {
        "token": str(access_token),
    }
    return Response(out_put_messege, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=('username', 'password',),
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
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


class UserViewSet(UserViewSet):
    @action(methods=['post', ], detail=False, permission_classes=(AllowAny, ))
    def reset_password_confirm_code(self, request, *args, **kwargs):

        serializer = EmailAndTokenSerializer(data={
                'email': request.email,
                'confirmation_code': request.confirmation_code,
            }
        )
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(email=request.email)
            is_token_valid = user.code_owner.get(
                confirmation_code=request.confirmation_code)
            is_token_valid.is_confirmed = True
            is_token_valid.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @action(['post'], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        user = User.objects.get(email=email)
        user.set_password(serializer.data["new_password"])
        user.code_owner.all().delete()
        """if hasattr(user, "last_login"):
            user.last_login = now()"""
        user.save()

        """if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)"""
        return Response(status=status.HTTP_204_NO_CONTENT)
