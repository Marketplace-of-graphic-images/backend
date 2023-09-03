from http import HTTPStatus

import pytest
from django.core import mail

from .utils import take_confirmation_code


@pytest.mark.django_db(transaction=True)
class Test00UserRegistration:
    url_signup = '/api/v1/auth/signup/'
    url_signup_confirmation = '/api/v1/auth/signup-confirmation/'
    url_signin = '/api/v1/auth/signin/'
    url_signout = '/api/v1/auth/signout/'

    def test_00_nodata_signup(self, client):
        response = client.post(self.url_signup)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signup}`, '
            'не содержит необходимых данных, должен вернуться ответ со '
            'статусом 400.'
        )
        response_json = response.json()
        empty_fields = ('email', 'username', 'password',)
        for field in empty_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в POST-запросе к `{self.url_signup}` не переданы '
                'необходимые данные, в ответе должна возвращаться информация '
                'об обязательных для заполнения полях.'
            )

    def test_01_nodata_signup_confirmation(self, client):
        response = client.post(self.url_signup_confirmation)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signup}`, '
            'не содержит необходимых данных, должен вернуться ответ со '
            'статусом 400.'
        )
        response_json = response.json()
        empty_fields = ('email', 'username', 'password', 'confirmation_code',)
        for field in empty_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в POST-запросе к `{self.url_signup}` не переданы '
                'необходимые данные, в ответе должна возвращаться информация '
                'об обязательных для заполнения полях.'
            )

    def test_02_invalid_data_signup(self, client):
        outbox_before_count = len(mail.outbox)
        invalid_data = {
            'email': 'invalid_email',
            'username': ' ',
            'password': ' ',
        }

        response = client.post(self.url_signup, data=invalid_data)
        outbox_after_count = len(mail.outbox)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к эндпоинту `{self.url_signup}` содержит '
            'некорректные данные, должен вернуться ответ со статусом 400.'
        )
        assert outbox_before_count == outbox_after_count, (
            f'Проверьте, что POST-запрос к `{self.url_signup}` с '
            'некорректными данными не отправляет письмо на почту.'
        )

        response_json = response.json()
        invalid_fields = ['email', 'username', 'password']
        for field in invalid_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в  POST-запросе к `{self.url_signup}` переданы '
                'некорректные данные, в ответе должна возвращаться информация '
                'о неправильно заполненных полях.'
            )

        valid_email = 'validemail@pictura.fake'
        invalid_data = {
            'email': valid_email,
        }
        response = client.post(self.url_signup, data=invalid_data)
        outbox_after_count = len(mail.outbox)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к `{self.url_signup}` не содержит данных о '
            '`username` и `password`, должен вернуться ответ со статусом 400.'
        )
        assert outbox_before_count == outbox_after_count, (
            f'Проверьте, что POST-запрос к `{self.url_signup}`, не содержащий '
            'данных о `username` и `password`, не отправляет письмо на почту.'
        )

    def test_03_valid_data_user_signup(self, client, django_user_model):
        outbox_before_count = len(mail.outbox)
        valid_data = {
            'email': 'validemail@pictura.fake',
            'username': 'valid_username',
            'password': 'validpassword',
            'is_author': False,
        }

        response = client.post(self.url_signup, data=valid_data)
        outbox_after = mail.outbox
        confirmation_code = take_confirmation_code(outbox_after[0].body)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.json() == valid_data, (
            'POST-запрос с корректными данными, отправленный на эндпоинт '
            f'`{self.url_signup}`, должен вернуть ответ, содержащий '
            'информацию о `username`, `email`, `password` и `is_author` '
            'созданного пользователя.'
        )
        assert len(outbox_after) == outbox_before_count + 1, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signup}`, '
            f'содержит корректные данные - должен быть отправлен email'
            'с кодом подтвержения.'
        )
        assert valid_data['email'] in outbox_after[0].to, (
            'Если POST-запрос, отправленный на эндпоинт  '
            f'`{self.url_signup}`, содержит корректные данные - письмо с '
            'подтверждением должно отправляться на `email`, указанный в '
            'запросе.'
        )

        valid_data['confirmation_code'] = confirmation_code
        response = client.post(self.url_signup_confirmation, data=valid_data)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.cookies.get('jwt') is not None, (
            'POST-запрос с корректными данными, отправленный на эндпоинт '
            f'`{self.url_signup}`, должен вернуть ответ, содержащий '
            'cookies с `jwt`'
        )

        new_user = django_user_model.objects.filter(email=valid_data['email'])
        assert new_user.exists(), (
            'POST-запрос с корректными данными, отправленный на эндпоинт '
            f'`{self.url_signup}`, должен создать нового пользователя.'
        )

        new_user.delete()

    def test_04_user_with_same_data(self, client, user_client):
        valid_data = {
            'email': 'testuser@pictura.fake',
            'username': 'TestUser',
            'password': 'validpassword',
            'is_author': False,
        }

        response = client.post(self.url_signup, data=valid_data)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте, чтобы запрос на эндпоинт `{self.url_signup}` выводил '
            'ошибку, при попытке создать user с уже существующими данными: '
            f'{response.json()}'
        )

        valid_data = {
            'email': 'testuser@pictura.fake',
            'username': 'TestUser1',
            'password': 'validpassword',
            'is_author': False,
        }
        response = client.post(self.url_signup, data=valid_data)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте, чтобы запрос на эндпоинт `{self.url_signup}` выводил '
            'ошибку, при попытке создать user с уже существующими данными: '
            f'{response.json()}'
        )

    def test_05_signin_no_data(self, client, user_client):
        response = client.post(self.url_signin)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signin}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signin}`, '
            'не содержит необходимых данных, должен вернуться ответ со '
            'статусом 400.'
        )
        response_json = response.json()
        empty_fields = ('email', 'password',)
        for field in empty_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в POST-запросе к `{self.url_signin}` не переданы '
                'необходимые данные, в ответе должна возвращаться информация '
                'об обязательных для заполнения полях.'
            )

    def test_06_invalid_data_signin(self, client, user_client):
        valid_data = {
            'email': 'testuser1@pictura.fake',
            'password': 'TestUser',
        }
        response = client.post(self.url_signin, data=valid_data)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signin}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signin}`, '
            'содержит неверный email, должен вернуться ответ со '
            'статусом 400.'
        )

        valid_data = {
            'username': 'TestUser',
            'password': 'TestUser',
        }
        response = client.post(self.url_signin, data=valid_data)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signin}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signin}`, '
            'содержит username вметос email, должен вернуться ответ со '
            'статусом 400.'
        )

        valid_data = {
            'email': 'testuser@pictura.fake',
            'password': 'TestUser1',
        }
        response = client.post(self.url_signin, data=valid_data)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signin}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос, отправленный на эндпоинт `{self.url_signin}`, '
            'содержит неверный пароль, должен вернуться ответ со '
            'статусом 400.'
        )

    def test_07_signin(self, client, user_client):
        valid_data = {
            'email': 'testuser@pictura.fake',
            'password': 'TestUser',
        }

        response = client.post(self.url_signin, data=valid_data)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signout}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.cookies.get('jwt') is not None, (
            'POST-запрос с корректными данными, отправленный на эндпоинт '
            f'`{self.url_signin}`, должен вернуть ответ, содержащий '
            'cookies с `jwt`'
        )

    def test_08_signout(self, user_client):

        response = user_client.post(self.url_signout)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signout}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'Проверьте, что запрос на эндпоинт `{self.url_signout}`'
            ' выполняется.'
        )
        assert response.cookies.get('jwt') != '', (
            f'POST-запрос отправленный на эндпоинт `{self.url_signout}` '
            ', должен отчистить куки, содержащие в себе jwt токен.'
        )
