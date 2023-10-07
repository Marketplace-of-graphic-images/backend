import logging
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent / 'infra/.env'
load_dotenv()


SECRET_KEY = 'django-insecure-c+@7f59vob3j5knjj&q)2btv2xx3985g@4rb1b4%jak#vyw1wc'


DEBUG = os.environ['DEBUG'] == 'True'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '80.87.107.75',
    'pictura.acceleratorpracticum.ru'
]

DJANGO_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
)

THIRD_PARTY_APPS = (
    'django_filters',
    'rest_framework',
    'phonenumber_field',
    'drf_yasg',
    'djoser',
    'social_django',
    'rest_framework_simplejwt',
    'corsheaders',
)

LOCAL_APPS = (
    'api',
    'images',
    'users',
    'core',
    'tags',
    'comments',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'marketgraphicimages.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'marketgraphicimages.wsgi.application'


if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv(
                'DB_ENGINE', default='django.db.backends.postgresql'
            ),
            'NAME': os.getenv('DB_NAME', 'postgres'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', 5432)
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'core.password_validation.InvalidCharactersValidator',
    },
    {
        'NAME': 'core.password_validation.CyrillicLettersValidator',
    },
    {
        'NAME': 'core.password_validation.EasyPasswordValidator',
    },
    {
        'NAME': 'core.password_validation.MaximumLengthValidator',
    },
    {
        'NAME': 'core.password_validation.TheSamePasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "users.User"

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "core.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


IMAGES_RECOMENDED_SIZE = 8
IMAGES_LIMIT_SIZE = 10
MAX_NUM_OF_TAGS_RECOMENDED_COMBO = 4
ALLOWED_EXTENSIONS = [
    'jpeg', 'jpg,' 'png', 'webp', 'raw', 'tiff', 'psd', 'gif', 'svg'
]

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")
EMAIL_BACKEND_NAME = "Anonim-not-found@yandex.ru"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
}

white_list = [
    'http://127.0.0.1:8000/',
    'http://127.0.0.1:8000/api/v1/accounts/profile/',
    'https://80.87.107.75:8000/api/v1/accounts/profile/',
    'http://pictura.acceleratorpracticum.ru/api/v1/accounts/profile/',
    'https://pictura.acceleratorpracticum.ru/api/v1/accounts/profile/',
]

DJOSER = {
    'LOGIN_FIELD': 'email',
    'SEND_CONFIRMATION_EMAIL': True,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
    'SERIALIZERS': {
        'password_reset_confirm': 'users.serializers.PasswordSerializer',
        'password_reset_confirm_code': 'users.serializers.EmailAndTokenSerializer',
        'user': 'api.v1.serializers.UserSerializer',
        'current_user': 'api.v1.serializers.UserSerializer',

    },
    'EMAIL': {
        'password_reset': 'core.new_password_reset_email.PasswordResetEmail',
    },
    'PERMISSIONS': {
        'password_reset_confirm_code': ['rest_framework.permissions.AllowAny'],
        'user': ['core.permissions.CurrentUserOrReadOnlyOrAdmin'],
        'short_me': ['rest_framework.permissions.IsAuthenticated'],
    },
    'SOCIAL_AUTH_TOKEN_STRATEGY': 'djoser.social.token.jwt.TokenStrategy',
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': white_list,
    'TOKEN_MODEL': None,
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.yandex.YandexOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_YANDEX_OAUTH2_KEY = os.getenv('YANDEX_KEY')

SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = os.getenv('YANDEX_SECRET')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_PROJECT_CX = os.getenv('GOOGLE_PROJECT_CX')

os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
LOGS_DIR = os.path.join(BASE_DIR, 'logs', 'marketgraphicimages.log')
FORMAT_LOGRECORD = (
    '%(asctime)s [%(levelname)s], %(name)s '
    '%(funcName)s: %(message)s'
)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_format': {
            'format': FORMAT_LOGRECORD,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'main_format',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'main_format',
            'filename': LOGS_DIR,
            'mode': 'w',
            'encoding': 'utf-8',
            'backupCount': 5,
            'maxBytes': 4999999
        },
    },
    'loggers': {
        'main': {
            'handlers': ['console', 'file', ],
            'level': 'INFO' if not DEBUG else 'DEBUG',
            'propagrate': True,
        },
        'django': {
            'handlers': ['console', 'file', ],
            'level': 'INFO',
            "propagate": True,
        },
    },
}
logger = logging.getLogger('main')

if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'skvmrelay.netangels.ru'
    EMAIL_PORT = 25
    #EMAIL_USE_SSL = True
    #EMAIL_HOST_USER = EMAIL_BACKEND_NAME
    #EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = EMAIL_BACKEND_NAME

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'https://marketplace-of-graphic-images.github.io',
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

CORS_ALLOWED_ORIGINS = (
    'http://localhost:3000',
    'https://marketplace-of-graphic-images.github.io',
)
CORS_ALLOWED_ORIGIN_REGEXES = (
    'http://localhost:3000',
    'https://marketplace-of-graphic-images.github.io',
)
