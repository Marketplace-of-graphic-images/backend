from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers

from core.utils import verify_value

User = get_user_model()


class EmailAndTokenSerializer(serializers.Serializer):
    """Validate email and confirmation code.
    Сhecks the confirmation code.
    """

    confirmation_code = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data: dict) -> dict:
        confirmation_code = data.get('confirmation_code', '')
        try:
            user = User.objects.get(email=data.get('email', ''))
            data['user'] = user
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError(
                {'email': 'invalid_email'},
            )
        data['user_confirm_code'] = user.code_owner.get()
        if verify_value(confirmation_code,
                        data['user_confirm_code'].confirmation_code):
            return data
        else:
            raise serializers.ValidationError(
                {'token': 'invalid token'},
            )


class PasswordSerializer(serializers.Serializer):
    """Сhecks that the confirmation code is confirmed.
    Validate email and password.
    """
    new_password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.EmailField()

    def validate(self, data: dict) -> dict:
        try:
            user = User.objects.get(email=data.get('email'))
            data['user'] = user
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError(
                {'email': 'invalid_email'},
            )
        if not user.code_owner.get().is_confirmed:
            raise serializers.ValidationError(
                {'confirmation_code': 'confirmation code is not confirmed'}
            )
        try:
            validate_password(data["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(data)
