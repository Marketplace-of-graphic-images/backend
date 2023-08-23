from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import ConfirmationCode

User = get_user_model()


class AuthSignUpSerializer(serializers.ModelSerializer):
    is_author = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'is_author')

    def validate(self, data):
        """
        Validates the given data.

        Args:
            data (dict): The data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            ValidationError: If the username is "me".
            ValidationError: If the user with this email already exist.
        """
        if User.objects.filter(username=data.get('username'),
                               email=data.get('email')).exists():
            raise ValidationError(_('User with this email already exist'))
        if data.get('username').lower() == 'me':
            raise ValidationError(_('Username cannot be "me"'))
        return data


class ConfirmationSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=True)
    is_author = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password',
                  'is_author', 'confirmation_code')

    def validate(self, data):
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
                                       email=data.get("email"))
        confirmation_code = data.get("confirmation_code")
        if email_user.confirmation_code != int(confirmation_code):
            raise ValidationError(_("Invalid confirmation code"))
        user = self.create_user(data)
        email_user.delete()
        return user
    
    def create_user(self, data):
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
            user, _ = User.objects.get_or_create(
                username=data.get('username'),
                email=data.get('email'),
                author=(data.get('is_author')),
        )
        except IntegrityError:
            raise ValidationError(
            "Пользователь с такими данными уже существует"
        )
        user.set_password(data.get('password'))
        user.save()
        return user
        


class AuthSignInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, data):
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
        user = User.objects.filter(email=data.get("email"))
        if user.exists() and user.first().check_password(data.get("password")):
            return user.first()
        raise ValidationError(_("Invalid credentials"))
