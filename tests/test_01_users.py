from http import HTTPStatus

import pytest
from django.core import mail
from rest_framework.test import APIClient


@pytest.mark.django_db(transaction=True)
class Test00UserSetResetPassword:
    url_reset_password = '/api/v1/users/reset_password/'
    url_password_confirm_code = '/api/v1/users/reset_password_confirm_code/'
    url_reset_password_confirm = '/api/v1/users/reset_password_confirm/'
    url_set_password = '/api/v1/users/set_password/'

    @pytest.mark.parametrize("url_unit, expected_result", [
        (url_reset_password, HTTPStatus.UNAUTHORIZED),
        (url_password_confirm_code, HTTPStatus.UNAUTHORIZED),
        (url_reset_password_confirm, HTTPStatus.UNAUTHORIZED),
        (url_set_password, HTTPStatus.UNAUTHORIZED),
    ])
    def test_00_urls_status(self, url_unit, expected_result):
        response = APIClient().get(url_unit)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт `{url_unit}` не найден. Проверьте '
            'настройки в *urls.py*.'
        )
        assert response.status_code == expected_result, (
            f'Эндпоинт `{url_unit}` не доступен. Проверьте '
            'настройки в *urls.py*.'
        )

    @pytest.mark.parametrize("url_unit, expected_fields", [
        (url_reset_password, ('email',)),
        (url_password_confirm_code, ('email', 'confirmation_code')),
        (url_reset_password_confirm, ('email', 'new_password')),
    ])
    def test_01_reset_password_chain_empty_fields(
        self,
        client,
        url_unit,
        expected_fields
    ):
        response = client.post(url_unit)
        response_json = response.json()

        for field in expected_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в POST-запросе к `{url_unit}` '
                'не переданы необходимые данные, в ответе должна '
                'возвращаться информация об обязательных для заполнения полях.'
            )

    @pytest.mark.parametrize("url_unit, invalid_data, expected_fields", [
        (url_reset_password, {'email': 'invalid_email'}, ('email',)),
        (url_password_confirm_code, {
            'email': 'invalid_email',
            'confirmation_code': 'invalid_confirmation_code'},
            ('email',)),
        (url_password_confirm_code, {
            'email': 'testuser@pictura.fake',
            'confirmation_code': 'invalid_confirmation_code'},
            ('confirmation_code',)),
        (url_reset_password_confirm, {
            'new_password': '1*_пinvalid_new_password',
            'email': 'invalid_email'},
            ('email',)),
        (url_reset_password_confirm, {
            'new_password': '1*_пinvalid_new_password',
            'email': 'testuser@pictura.fake'},
            ('confirmation_code',)),
    ])
    def test_02_reset_password_chain_invalid_data(
        self,
        client,
        url_unit,
        invalid_data,
        expected_fields,
        user_client,
        user_confirmation_code,
    ):
        outbox_before_count = len(mail.outbox)
        response = client.post(url_unit, data=invalid_data)
        outbox_after_count = len(mail.outbox)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Если POST-запрос к эндпоинту `{url_unit}` '
            'содержит некорректные данные, должен вернуться ответ '
            'со статусом 400.'
        )
        assert outbox_before_count == outbox_after_count, (
            f'Проверьте, что POST-запрос к `{url_unit}` с '
            'некорректными данными не отправляет письмо на почту.'
        )

        response_json = response.json()
        for field in expected_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в  POST-запросе к `{url_unit}` переданы '
                'некорректные данные, в ответе должна возвращаться информация '
                'о неправильно заполненных полях.'
            )

    def test_03_reset_reset_password_confirm_valid_data(
        self,
        client,
        user_client,
        user_confirmation_code_is_confirmed,
        hash_confirm_code,
    ):
        valid_data = {
            'new_password': 'valid_new_password12',
            'email': 'testuser@pictura.fake'
        }
        response = client.post(
            self.url_reset_password_confirm,
            data=valid_data
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'Если POST-запрос к `{self.url_reset_password_confirm}` '
            'содержит корректные данные, должен вернуться ответ '
            'со статусом 204.'
        )

    @pytest.mark.parametrize("url_unit, valid_data", [
        (url_reset_password, {'email': 'testuser@pictura.fake'}),
        (url_password_confirm_code, {
            'email': 'testuser@pictura.fake',
            'confirmation_code': '123456'})
    ])
    def test_04_reset_password_chain_valid_data(
        self,
        client,
        url_unit,
        valid_data,
        user_client,
        user_confirmation_code,
    ):
        response = client.post(url_unit, data=valid_data)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'Если POST-запрос к эндпоинту `{url_unit}` '
            'содержит корректные данные, должен вернуться ответ '
            'со статусом 204.'
        )

    def test_05_set_password(self, user_client,):
        valid_data = {
            'new_password': 'newpassword5431',
            'current_password': 'TestUser',
        }
        response = user_client.post(self.url_set_password, data=valid_data)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'Пароль по {self.url_set_password} не изменен.'
        )

    @pytest.mark.parametrize("url_unit, invalid_data, expected_fields", [
        (url_set_password,
         {'new_password': 'newpassword5431',
          'current_password': 'feff'},
         ('current_password',)),
        (url_set_password,
         {'new_password': '',
          'current_password': 'TestUser'},
         ('new_password',)),
    ])
    def test_06_set_password_invalid_data(
        self,
        user_client,
        url_unit,
        invalid_data,
        expected_fields,
    ):
        response = user_client.post(url_unit, data=invalid_data)
        response_json = response.json()
        for field in expected_fields:
            assert (field in response_json
                    and isinstance(response_json.get(field), list)), (
                f'Если в  POST-запросе к `{url_unit}` переданы '
                'некорректные данные, в ответе должна возвращаться информация '
                'о неправильно заполненных полях.'
            )

    def test_07_reset_password_send_mail(
        self,
        client,
        user_client
    ):
        valid_data = {'email': 'testuser@pictura.fake'}
        outbox_before_count = len(mail.outbox)
        client.post(
            self.url_reset_password,
            data=valid_data
        )
        outbox_after_count = len(mail.outbox)
        assert outbox_before_count + 1 == outbox_after_count, (
            f'Проверьте, что POST-запрос к `{self.url_reset_password}` '
            'с корректными данными отправляет письмо на почту.'
        )