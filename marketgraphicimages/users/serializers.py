from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class EmailAndTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email", "")
        token = data.get("token", "")
        try:
            user = User.objects.get(email=email)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_email"
            raise ValidationError(
                {"email": [self.error_messages[key_error]]}, code=key_error
            )
        is_token_valid = user.code_owner.get(token=token)
        if is_token_valid:
            """is_token_valid.is_confirmed = True
            is_token_valid.save()"""
            return data
        else:
            key_error = "invalid_token"
            raise ValidationError(
                {"token": [self.error_messages[key_error]]}, code=key_error
            )


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user = (User.objects.get(email=getattr(self, "email", None)) or
                User.objects.get(email=self.context["request"].email))
        # why assert? There are ValidationError / fail everywhere
        assert user is not None
        token = getattr(self, "token", None) or self.context["request"].token
        if not user.code_owner.get(token=token).is_confirmed:
            raise serializers.ValidationError({'token': 'код не подтвержден'})
        try:
            validate_password(attrs["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return super().validate(attrs)
