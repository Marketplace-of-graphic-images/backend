from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.paginator import Paginator
from django.db import IntegrityError, models, transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from marketgraphicimages.settings import (
    COMMENTS_PAGINATOR_SIZE,
    MAX_NUM_OF_TAGS_RECOMENDED_COMBO,
    NUM_OF_RECOMMENDED_IMAGES,
    NUM_OTHER_AUTHOR_IMAGES,
)

from comments.models import Comment
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


class BaseShortUserSerializer(serializers.ModelSerializer):
    """Base serializer for user class."""

    is_author = serializers.BooleanField(source='author')

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_photo', 'is_author')


class AuthorSerializer(BaseShortUserSerializer):
    """Serializer for image author user model."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    num_of_author_images = serializers.SerializerMethodField(
        method_name='get_num_of_author_images'
    )

    class Meta(BaseShortUserSerializer.Meta):
        fields = BaseShortUserSerializer.Meta.fields + (
            'num_of_author_images', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Checking if the user is subscribed to the specified author."""

        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=user, author=obj).exists()
        return False

    def get_num_of_author_images(self, obj):
        """Getting the number of published images of an author."""

        return obj.images.count()


class CommentatorShortSerializer(BaseShortUserSerializer):
    """Serializer for commentator user model."""

    pass


class CommentShortSerializer(serializers.ModelSerializer):
    """Serializer for comment model on image page."""

    commentator = CommentatorShortSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created', 'commentator')


class ImageShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'name', 'image', 'tags')


class ImageGetSerializer(serializers.ModelSerializer):
    """Image model serializer for get requests."""

    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    comments = serializers.SerializerMethodField(
        method_name='get_paginated_comments'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    recommended = serializers.SerializerMethodField(
        method_name='get_recommended'
    )
    other_author_images = serializers.SerializerMethodField(
        method_name='get_other_author_images'
    )

    class Meta:
        model = Image
        fields = (
            'id', 'created', 'author', 'name', 'image', 'license', 'price',
            'format', 'tags', 'is_favorited', 'comments', 'recommended',
            'other_author_images'
        )

    def get_is_favorited(self, obj):
        """Checking if the specified image is in the favorites list."""

        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteImage.objects.filter(image=obj, user=user).exists()
        return False

    def get_paginated_comments(self, obj):
        """Own method for getting paginated list of comments based on
        COMMENTS_PAGINATOR_SIZE params from settings.py."""

        page_size = self.context['request'].query_params.get(
            'size', COMMENTS_PAGINATOR_SIZE
        )
        paginator = Paginator(obj.comments.all(), page_size)
        page = self.context['request'].query_params.get('page', 1)
        comments = paginator.page(page)
        serializer = CommentShortSerializer(comments, many=True)
        return serializer.data

    def get_recommended(self, obj):
        """Getting a list of recommendations based on tags and
        returns the number of images specified in the
        NUM_OF_RECOMMENDED_IMAGES, randomly selected."""

        tags = Tag.objects.filter(
            id__in=obj.tags.all()
        ).annotate(
            image_count=models.Count('tagimage')
        ).order_by(
            '-image_count'
        )[:MAX_NUM_OF_TAGS_RECOMENDED_COMBO]
        images = Image.objects.none()
        for сombination in range(tags.count(), 0, -1):
            new_images = Image.objects.annotate(
                num_of_tags=models.Count(
                    'tags', filter=models.Q(tags__in=tags[:сombination])
                )
            ).filter(
                num_of_tags=сombination
            ).exclude(
                id=obj.id
            ).exclude(
                id__in=images
            ).order_by(
                '?'
            ).distinct()
            images = images | new_images
            if images.count() >= NUM_OF_RECOMMENDED_IMAGES:
                break
        images = images[:NUM_OF_RECOMMENDED_IMAGES]
        serializer = ImageShortSerializer(images, many=True)
        return serializer.data

    def get_other_author_images(self, obj):
        """Getting other works of the authorbased on tags and
        returns the number of images specified in the
        NUM_OTHER_AUTHOR_IMAGES, randomly selected."""

        images = Image.objects.filter(
            author=obj.author).exclude(
                id=obj.id).order_by('?')[:NUM_OTHER_AUTHOR_IMAGES]
        serializer = ImageShortSerializer(images, many=True)
        return serializer.data


class CustomBase64ImageField(Base64ImageField):
    """Custom Base64ImageField with swagger_schema_fields."""

    class Meta:
        swagger_schema_fields = {
            'type': 'string',
            'title': 'Image Content',
            'description': 'Content of the image base64 encoded',
            'read_only': False
        }


class ImagePostPutPatchSerializer(serializers.ModelSerializer):
    """Image model serializer for post, put, patch requests."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = CustomBase64ImageField()

    class Meta:
        model = Image
        fields = ('name', 'image', 'license', 'price', 'tags', )
        read_only_fields = ('author', )

    def to_representation(self, instance):
        serializer = ImageGetSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    @staticmethod
    def get_extension(validated_data):
        """Method for getting file extension from validated data."""

        extension = validated_data['image'].content_type.split('/')[-1]
        return extension.upper()

    @transaction.atomic
    def create(self, validated_data):
        """Modified object creation method that gets file extension
        information and creates entries in the TagImage table."""

        tags = validated_data.pop('tags')
        validated_data['format'] = self.get_extension(validated_data)
        new_image = Image.objects.create(**validated_data)
        new_image.tags.set(tags)
        return new_image

    @transaction.atomic
    def update(self, instance, validated_data):
        """Modified object editing method that gets file extension
        information and edit entries in the TagImage table."""

        if 'tags' in validated_data:
            TagImage.objects.filter(image=instance).delete()
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        if 'image' in validated_data:
            validated_data['format'] = self.get_extension(validated_data)
        super().update(instance, validated_data)
        return instance
