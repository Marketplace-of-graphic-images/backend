from django.utils.version import get_version


assert (get_version()) == '4.2', 'Пожалуйста, используйте версию Django 4.2'

pytest_plugins = [
    'tests.fixture_user',
]
