from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from core.encryption_str import verify_value
from core.validators import validate_email
from users.models import ConfirmationCode

User = get_user_model()


class AuthSignUpSerializer(serializers.ModelSerializer):
    is_author = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'is_author')

    def validate(self, data: dict) -> dict:
        """
        Validate the given data.

        Args:
            data (dict): The data to be validated.

        Returns:
            dict: The validated data, if the password is valid.
        """
        validate_password(data.get('password'))
        validate_email(data.get('email'))
        return data


class ConfirmationSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=True)
    is_author = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password',
                  'is_author', 'confirmation_code')

    def validate(self, data: dict) -> dict:
        """
        Validate the user by checking the provided confirmation code
        against the user's confirmation code.

        Args:
            data (dict): A dictionary containing the user's email
            and confirmation code.

        Returns:
            User: The validated User object.

        Raises:
            ValidationError: If the provided confirmation code is invalid.
        """
        email_user = get_object_or_404(ConfirmationCode,
                                       email=data.get('email'))
        confirmation_code = data.get('confirmation_code')
        if not verify_value(confirmation_code, email_user.confirmation_code):
            raise ValidationError(
                detail={'errors': _('Invalid confirmation code')},
                code=status.HTTP_400_BAD_REQUEST,
            )
        user = self.create_user(data)
        email_user.delete()
        data['user'] = user
        return data

    def create_user(self, data: dict) -> User:
        """
        Create user.

        Args:
            data (dict): A dictionary containing the user's options.

        Returns:
            User: The created User object.

        Raises:
            ValidationError: If the user with this email already exist.
        """
        try:
            user = User.objects.create(
                username=data.get('username'),
                email=data.get('email'),
                author=(data.get('is_author')),
            )
        except IntegrityError:
            raise ValidationError(
                detail={'errors': _('User with this data already exist')},
                code=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(data.get('password'))
        user.save()
        return user


class AuthSignInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('password')

    def validate(self, data: dict) -> dict:
        """
        Validates the given data by checking if a user with the provided
        email exists and if the provided password is correct for that user.

        Parameters:
            - data (dict): A dictionary containing the email and password
            to be validated.

        Returns:
            - User: The User object if the credentials are valid.

        Raises:
            - ValidationError: If the provided credentials are invalid.
        """
        try:
            user = User.objects.get(email=data.get('email'))
        except User.DoesNotExist:
            raise ValidationError(
                detail={'errors': _('User with this email does not exist')},
                code=status.HTTP_404_NOT_FOUND,
            )
        else:
            if user.check_password(data.get("password")):
                data['user'] = user
                return data
            raise ValidationError(
                detail={'errors': _('Wrong password')},
                code=status.HTTP_400_BAD_REQUEST,
            )
