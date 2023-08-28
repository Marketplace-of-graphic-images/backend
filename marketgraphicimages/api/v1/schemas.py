from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title='Pictura API',
      default_version='v1',
      description=(
          'API для сервиса по размещению и продаже '
          'изображений под названием Pictura'
        ),
      terms_of_service='https://www.google.com/policies/terms/',
      contact=openapi.Contact(email='contact@snippets.local'),
      license=openapi.License(name='BSD License'),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

SIGUP_SHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=('username', 'email', 'password', 'is_author'),
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, min_length=8),
        'is_author': openapi.Schema(
            type=openapi.TYPE_BOOLEAN, default=False
        ),
    },
)

SIGUP_SHEMA_CONFIRMATION = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=(
        'username', 'email', 'password',
        'is_author', 'confirmation_code',
    ),
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, min_length=8),
        'is_author': openapi.Schema(
            type=openapi.TYPE_BOOLEAN, default=False
        ),
        'confirmation_code': openapi.Schema(
            type=openapi.TYPE_STRING, pattern=r'^\d+$', max_length=6
        ),
    },
)

SIGNIN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=('email', 'password',),
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, min_length=8),
    },
)

TOKEN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=('access_token',),
    properties={
        'access_token': openapi.Schema(type=openapi.TYPE_STRING),
    }
)
