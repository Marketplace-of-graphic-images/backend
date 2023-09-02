from http import HTTPStatus

import pytest


@pytest.mark.django_db(transaction=True)
class Test00UserRegistration:
    url_signup = '/api/v1/auth/signup/'

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

    def test_00_invalid_data_signup(self, client, django_user_model):
        invalid_data = {
            'email': 'invalid_email',
            'username': ' ',
            'password': ' ',
        }
        users_count = django_user_model.objects.count()

        response = client.post(self.url_signup, data=invalid_data)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{self.url_signup}` не найден. Проверьте настройки '
            'в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к эндпоинту `{self.url_signup}` содержит '
            'некорректные данные, должен вернуться ответ со статусом 400.'
        )
        assert users_count == django_user_model.objects.count(), (
            f'Проверьте, что POST-запрос к `{self.url_signup}` с '
            'некорректными данными не создаёт нового пользователя.'
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
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к `{self.url_signup}` не содержит данных о '
            '`username` и `password`, должен вернуться ответ со статусом 400.'
        )
        assert users_count == django_user_model.objects.count(), (
            f'Проверьте, что POST-запрос к `{self.url_signup}`, не содержащий '
            'данных о `username` и `password`, не создаёт нового пользователя.'
        )

        valid_username = 'validusername'
        invalid_data = {
            'username': valid_username,
        }
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к `{self.url_signup}` не содержит данных о '
            '`email` и `password`, должен вернуться ответ со статусом 400.'
        )
        assert users_count == django_user_model.objects.count(), (
            f'Проверьте, что POST-запрос к `{self.url_signup}`, не содержащий '
            'данных о `email` и `password`, не создаёт нового пользователя.'
        )

        valid_password = 'validpassword'
        invalid_data = {
            'password': valid_password,
        }
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к `{self.url_signup}` не содержит данных о '
            '`email` и `username`, должен вернуться ответ со статусом 400.'
        )
        assert users_count == django_user_model.objects.count(), (
            f'Проверьте, что POST-запрос к `{self.url_signup}`, не содержащий '
            'данных о `email` и `username`, не создаёт нового пользователя.'
        )
