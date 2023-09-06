import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from core.encryption_str import verify_value
from core.validators import validate_email
from images.models import FavoriteImage, Image, TagImage
from tags.models import Tag
from users.models import ConfirmationCode, Subscription

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


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class UserShortSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    num_of_author_images = serializers.SerializerMethodField(
        method_name='get_num_of_author_images'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'num_of_author_images', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=user, author=obj).exists()
        return False

    def get_num_of_author_images(self, obj):
        return obj.images.count()


class ImageGetSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )

    class Meta:
        model = Image
        fields = (
            'id', 'created', 'author', 'name', 'image', 'license', 'price',
            'format', 'tags', 'is_favorited'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteImage.objects.filter(image=obj, user=user).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ImagePostPutPatchSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Image
        fields = ('author', 'name', 'image', 'license', 'price', 'tags')

    def to_representation(self, instance):
        serializer = ImageGetSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    @staticmethod
    def get_extension(validated_data):
        extension = validated_data['image'].content_type.split('/')[-1]
        return extension.upper()

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        validated_data['format'] = self.get_extension(validated_data)
        new_image = Image.objects.create(**validated_data)
        for tag in tags:
            TagImage.objects.create(image=new_image, tag=tag)
        return new_image

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            TagImage.objects.filter(image=instance).delete()
            tags = validated_data.pop('tags')
            for tag in tags:
                TagImage.objects.create(image=instance, tag=tag)
        if 'image' in validated_data:
            validated_data['format'] = self.get_extension(validated_data)
        super().update(instance, validated_data)
        return instance
