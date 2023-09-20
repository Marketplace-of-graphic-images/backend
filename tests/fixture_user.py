
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from core.encryption_str import hash_value
from users.models import UserConfirmationCode


@pytest.fixture
def user_superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestSuperuser',
        email='testsuperuser@pictura.fake',
        password='TestSuperuser',
        author=False,
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        email='testuser@pictura.fake',
        password='TestUser',
        author=False,
    )


@pytest.fixture
def token_user_superuser(user_superuser):
    token = AccessToken.for_user(user_superuser)
    return {
        'jwt': str(token),
    }


@pytest.fixture
def user_superuser_client(token_user_superuser):
    client = APIClient()
    client.cookies['jwt'] = token_user_superuser['jwt']
    return client


@pytest.fixture
def token_user(user):
    token = AccessToken.for_user(user)
    return {
        'jwt': str(token),
    }


@pytest.fixture
def user_client(token_user):
    client = APIClient()
    client.cookies['jwt'] = token_user['jwt']
    return client


@pytest.fixture(scope="session")
def hash_confirm_code():
    value = hash_value('123456')
    return value

@pytest.fixture
def user_confirmation_code(user, hash_confirm_code):
    return UserConfirmationCode.objects.create(
        user=user,
        confirmation_code=hash_confirm_code,
    )

@pytest.fixture
def user_confirmation_code_is_confirmed(user, hash_confirm_code):
    return UserConfirmationCode.objects.create(
        user=user,
        confirmation_code=hash_confirm_code,
        is_confirmed=True
    )