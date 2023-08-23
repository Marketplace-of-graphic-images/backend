from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        """
        if data.get('username').lower() == 'me':
            raise ValidationError(_('Username cannot be "me"'))
        return data


class ConfirmationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("confirmation_code", "username")

    def validate(self, data):
        """
        Validate the user by checking the provided confirmation code
        against the user's confirmation code.

        Args:
            data (dict): A dictionary containing the user's username
            and confirmation code.

        Returns:
            User: The validated User object.

        Raises:
            ValidationError: If the provided confirmation code is invalid.
        """

        user = get_object_or_404(User, username=data.get("username"))
        confirmation_code = data.get("confirmation_code")
        if user.confirmation_code != int(confirmation_code):
            raise ValidationError(_("Invalid confirmation code"))
        return user


class AuthSignInSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def validate(self, data):
        """
        Validates the given data by checking if a user with the provided
        username exists and if the provided password is correct for that user.

        Parameters:
            - data (dict): A dictionary containing the username and password
            to be validated.

        Returns:
            - User: The User object if the credentials are valid.

        Raises:
            - ValidationError: If the provided credentials are invalid.
        """
        user = User.objects.filter(username=data.get("username"))
        if user.exists() and user.first().check_password(data.get("password")):
            return user.first()
        raise ValidationError(_("Invalid credentials"))


# from djoser.serializers import UserFunctionsMixin, get_user_email_field_name


# class SendCodeResetSerializer(serializers.Serializer, UserFunctionsMixin):

#     email = serializers.EmailField(required=True)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.email_field = get_user_email_field_name(User)
