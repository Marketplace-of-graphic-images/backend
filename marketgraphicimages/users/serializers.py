from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers

User = get_user_model()


class EmailAndTokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        confirmation_code = data.get('confirmation_code', '')
        try:
            user = User.objects.get(email=data.get('email', ''))
            data['user'] = user
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError(
                {'email': 'invalid_email'},
            )
        is_token_valid = user.code_owner.get(
            confirmation_code=confirmation_code)
        if is_token_valid:
            return data
        else:
            raise serializers.ValidationError(
                {'token': 'invalid token'},
            )


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    email = serializers.EmailField()

    def validate(self, data):
        user = User.objects.get(email=data.get('email'))
        data['user'] = user
        assert user is not None
        confirmation_code = user.code_owner.get().confirmation_code
        if not user.code_owner.get(confirmation_code=confirmation_code
                                   ).is_confirmed:
            raise serializers.ValidationError(
                {'confirmation_code': 'confirmation code is not confirmed'}
            )
        try:
            validate_password(data["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )
        return super().validate(data)
