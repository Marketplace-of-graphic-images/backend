import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-c+@7f59vob3j5knjj&q)2btv2xx3985g@4rb1b4%jak#vyw1wc'

DEBUG = True

ALLOWED_HOSTS = []

DJANGO_APPS = (
    'corsheaders',
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
)

LOCAL_APPS = (
    'api',
    'images',
    'users',
    'core',
    'tags',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

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

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")
EMAIL_BACKEND_NAME = "sistem@server.ru"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
}

white_list = [
    'http://127.0.0.1:8000/',
    'http://127.0.0.1:8000/api/v1/accounts/profile/',
]

DJOSER = {
    'LOGIN_FIELD': 'email',
    'SEND_CONFIRMATION_EMAIL': True,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
    'SERIALIZERS': {
        'password_reset_confirm': 'users.serializers.PasswordSerializer',
        'password_reset_confirm_code': 'users.serializers.EmailAndTokenSerializer',
    },
    'EMAIL': {
        'password_reset': 'core.new_password_reset_email.PasswordResetEmail',
    },
    'PERMISSIONS': {
        'password_reset_confirm_code': ['rest_framework.permissions.AllowAny'],
    },
    'SOCIAL_AUTH_TOKEN_STRATEGY': 'djoser.social.token.jwt.TokenStrategy',
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': white_list,
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.yandex.YandexOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_YANDEX_OAUTH2_KEY = os.getenv('YANDEX_KEY')

SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = os.getenv('YANDEX_SECRET')
