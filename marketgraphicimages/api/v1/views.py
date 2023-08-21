from djoser import utils
from djoser.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
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
    # try:
    #     user, _ = User.objects.get_or_create(
    #         username=request.data.get('username'),
    #         email=request.data.get('email'),
    #         author=(serializer.validated_data.get('is_author')),
    #     )
    # except IntegrityError:
    #     return Response(
    #         "Пользователь с такими данными уже существует",
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )
    # user.set_password(serializer.validated_data.get('password'))
    # user.save()
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

class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """Use this endpoint to obtain user authentication token."""

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_200_OK
        )
