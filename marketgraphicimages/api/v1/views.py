from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .schemas import (
    LOGIN_DONE_SCHEMA,
    SIGNIN_SCHEMA,
    SIGNUP_DONE_SCHEMA,
    SIGUP_SHEMA,
    SIGUP_SHEMA_CONFIRMATION,
)
from api.v1.filters import ImageFilter
from api.v1.serializers import (
    AuthSignInSerializer,
    AuthSignUpSerializer,
    BaseShortUserSerializer,
    ConfirmationSerializer,
    ImageGetSerializer,
    ImagePostPutPatchSerializer,
    ImageShortSerializer,
    TagSerializer,
)
from core.confirmation_code import send_email_with_confirmation_code
from images.models import Image
from tags.models import Tag

User = get_user_model()

TOKEN_LIFETIME = int(
    django_settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', 0).total_seconds()
)


@swagger_auto_schema(
    method='post',
    request_body=SIGUP_SHEMA,
    responses={
        200: SIGUP_SHEMA,
        400: 'Bad request',
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def auth_signup_post(request: Request) -> Response:
    serializer = AuthSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    send_email_with_confirmation_code(request)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=SIGUP_SHEMA_CONFIRMATION,
    responses={
        200: SIGNUP_DONE_SCHEMA,
        400: 'Bad request',
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def auth_confirmation(request: Request) -> Response:
    serializer = ConfirmationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data.get('user')
    access_token = AccessToken.for_user(serializer.validated_data.get('user'))
    response = Response(
        BaseShortUserSerializer(user).data, status=status.HTTP_200_OK
    )
    response.set_cookie(
        'jwt', str(access_token), expires=TOKEN_LIFETIME, httponly=True
    )
    return response


@swagger_auto_schema(
    method='post',
    request_body=SIGNIN_SCHEMA,
    responses={
        200: LOGIN_DONE_SCHEMA,
        400: 'Bad request',
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_token_post(request: Request) -> Response:
    serializer = AuthSignInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data.get('user')
    access_token = AccessToken.for_user(serializer.validated_data.get('user'))
    response = Response(
        BaseShortUserSerializer(user).data, status=status.HTTP_200_OK
    )
    response.set_cookie(
        'jwt', str(access_token), expires=TOKEN_LIFETIME, httponly=True
    )
    return response


@api_view(['POST'])
def sign_out(_: Request) -> Response:
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('jwt')
    return response


class RedirectSocial(View):

    def get(self, request: Request, *args, **kwargs) -> Response:
        code, state = str(request.GET['code']), str(request.GET['state'])
        json_obj = {'code': code, 'state': state}
        return Response(json_obj)


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
                djoser_settings.PERMISSIONS.password_reset_confirm_code
            )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'reset_password_confirm_code':
            return djoser_settings.SERIALIZERS.password_reset_confirm_code
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
        if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': user}
            to = [serializer.validated_data.get('email')]
            djoser_settings.EMAIL.password_changed_confirmation(
                self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageViewSet(viewsets.ModelViewSet):
    """ViewSet to work with instances of images."""

    queryset = Image.objects.all()
    serializer_class = ImageGetSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ImageFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ImageGetSerializer
        if self.action == 'list':
            return ImageShortSerializer
        return ImagePostPutPatchSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all()
