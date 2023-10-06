from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
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
    FavoriteSerialiser,
    ImageGetSerializer,
    ImagePostPutPatchSerializer,
    ImageShortSerializer,
    TagSerializer,
)
from core.confirmation_code import send_email_with_confirmation_code
from core.permissions import (
    IsAuthorOrAdminPermission,
    OwnerOrAdminPermission,
    OwnerPermission,
)
from images.models import FavoriteImage, Image
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
    try:
        send_email_with_confirmation_code(request)
    except Exception as error:
        raise error
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
        'jwt', str(access_token), expires=TOKEN_LIFETIME,
        httponly=True, samesite='None', secure=True
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
        'jwt', str(access_token), expires=TOKEN_LIFETIME,
        httponly=True, samesite='None', secure=True
    )
    return response


@swagger_auto_schema(
    method='post',
    responses={
        204: '',
    },
)
@api_view(['POST'])
def sign_out(_: Request) -> Response:
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie('jwt')
    return response


class RedirectSocial(View):
    """
    Redirect for take 'code' and 'state' from social-auth/.
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        code, state = str(request.GET['code']), str(request.GET['state'])
        json_obj = {'code': code, 'state': state}
        return Response(json_obj)


class CustomUserViewSet(UserViewSet):
    """
    This viewset inherits from djoser `UserViewSet` and adds custom actions
    and permission handling for specific user operations, such as password
    reset confirmation.
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
    @swagger_auto_schema(responses={204: 'No Content', 400: 'Bad request'})
    def reset_password(self, request, *args, **kwargs):
        '''
        the method sends a confirmation code to an email
        if the email address exists.
        '''
        return super().reset_password(request, *args, **kwargs)

    @action(['post'], detail=False)
    @swagger_auto_schema(responses={204: 'No Content', 400: 'Bad request'})
    def reset_password_confirm_code(self, request, *args, **kwargs):
        """
        Checks the confirmation code.
        Update reset_password_confirm method.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            is_token_valid = serializer.validated_data.get('user_confirm_code')
            is_token_valid.is_confirmed = True
            is_token_valid.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(['post'], detail=False)
    @swagger_auto_schema(responses={204: 'No Content', 400: 'Bad request'})
    def reset_password_confirm(self, request, *args, **kwargs):
        """This method changes the password after successful
         confirmation of the code."""
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

    @action(['post'], detail=False)
    @swagger_auto_schema(responses={204: 'No Content', 400: 'Bad request'})
    def set_password(self, request, *args, **kwargs):
        return super().set_password(request, *args, **kwargs)

    def activation(self, request, *args, **kwargs):
        pass

    def resend_activation(self, request, *args, **kwargs):
        pass

    def reset_username(self, request, *args, **kwargs):
        pass

    def reset_username_confirm(self, request, *args, **kwargs):
        pass


class ImageViewSet(viewsets.ModelViewSet):
    """ViewSet to work with instances of images."""

    queryset = Image.objects.all()
    serializer_class = ImageGetSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ImageFilter
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ImageGetSerializer
        if self.action == 'list':
            return ImageShortSerializer
        return ImagePostPutPatchSerializer

    def get_permissions(self):
        method = self.request.method
        if self.action == 'favorite' and method == 'POST':
            return (IsAuthenticated(),)
        if method == 'DELETE':
            return (OwnerOrAdminPermission(),)
        if method == 'POST':
            return (IsAuthorOrAdminPermission(),)
        if method in ('PATCH', 'PUT',):
            return (OwnerPermission(),)
        return (IsAuthenticatedOrReadOnly(),)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete',),
            detail=True)
    def favorite(self, request, pk=None):
        """Add favorite image."""
        image = get_object_or_404(Image, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerialiser(data={
                'user': request.user.id,
                'image': image.id
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        if not image.favoriteimage_set.filter(user=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        favorite_image = get_object_or_404(
            FavoriteImage,
            image=image,
            user=self.request.user,
        )
        self.perform_destroy(favorite_image)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
            responses={200: 'Ok', 403: 'Only free image can be downloaded.'})
    @action(detail=True, methods=('get',))
    def download(self, request, pk=None):
        """Download an image."""
        image = self.get_object()
        if image.license != Image.LicenseType.FREE:
            return Response(
                {"errors": _("Only free image can be downloaded.")},
                status=status.HTTP_403_FORBIDDEN)
        response = FileResponse(open(image.image.path, 'rb'))
        response['Content-Disposition'] = (
            'attachment; filename="%s"' % _(image.image.name))
        response['Content-Length'] = image.image.size
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ['name', ]

    def get_queryset(self):
        return Tag.objects.all()
