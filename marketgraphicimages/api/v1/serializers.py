
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import IntegrityError, models, transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

from marketgraphicimages.settings import (
    IMAGES_LIMIT_SIZE,
    IMAGES_RECOMENDED_SIZE,
    MAX_NUM_OF_TAGS_RECOMENDED_COMBO,
)

from core.encryption_str import verify_value
from core.validators import validate_email
from images.models import FavoriteImage, Image, TagImage
from tags.models import Tag
from users.models import ConfirmationCode, Subscription

User = get_user_model()


class AuthSignUpSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

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
        validate_email(data.get('email'))
        try:
            validate_password(data.get('password'))
        except exceptions.ValidationError as error:
            raise exceptions.ValidationError({'password': error})
        return data


class ConfirmationSerializer(serializers.ModelSerializer):
    """Serializer for ending registration."""

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
                detail={'confirmation_code': _('Invalid confirmation code')},
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
                role=('Author' if data.get('is_author') else 'User'),
            )
        except IntegrityError:
            raise ValidationError(
                detail={'errors': _('User with this data already exist')},
            )
        user.set_password(data.get('password'))
        user.save()
        return user


class AuthSignInSerializer(serializers.Serializer):
    """Serializer for user login."""

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
        """
        try:
            user = User.objects.get(email=data.get('email'))
        except User.DoesNotExist:
            raise NotFound(
                detail={'email': _('User with this email does not exist')},
            )
        else:
            if user.check_password(data.get("password")):
                data['user'] = user
                return data
            raise ValidationError(
                detail={'password': _('Wrong password')},
            )


class BaseTagSerializer(serializers.ModelSerializer):
    """Base serializer for Tags model."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class TagShortSerializer(BaseTagSerializer):

    pass


class TagSerializer(BaseTagSerializer):
    """Serializer for Tag model."""
    tag_images = serializers.SerializerMethodField()

    def get_tag_images(self, obj):
        if self.context.get('request'):
            images = Image.objects.filter(tags=obj.id).order_by('?')[:1]
            serializer = ImageShortSerializer(
                images, many=True, context=self.context
            )
            return serializer.data

    class Meta(BaseTagSerializer.Meta):
        fields = BaseTagSerializer.Meta.fields + ('tag_images', )


class BaseShortUserSerializer(serializers.ModelSerializer):
    """Base serializer for user class."""

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_photo', 'role')


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
            'is_subscribed', 'num_of_author_images'
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


class ImageBaseSerializer(serializers.ModelSerializer):
    """Image model base serializer."""

    author = BaseShortUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(
            method_name='get_is_favorited'
        )

    class Meta:
        model = Image
        fields = (
            'id', 'created', 'author', 'name', 'image', 'is_favorited'
        )

    def get_is_favorited(self, obj):
        """Checking if the specified image is in the favorites list."""

        user = self.context.get('request').user
        if user.is_authenticated:
            return FavoriteImage.objects.filter(image=obj, user=user).exists()
        return False


class ImageShortSerializer(ImageBaseSerializer):
    """Serializer for short info about image."""

    pass


class ImageGetSerializer(ImageBaseSerializer):
    """Image model serializer for get requests."""

    author = AuthorSerializer(read_only=True)
    in_favorites = serializers.SerializerMethodField(
        method_name='get_in_favorites'
    )
    tags = TagShortSerializer(read_only=True, many=True)
    recommended = serializers.SerializerMethodField(
        method_name='get_recommended'
    )
    extension = serializers.SerializerMethodField(
        method_name='get_extension'
    )

    class Meta(ImageBaseSerializer.Meta):
        fields = ImageBaseSerializer.Meta.fields + (
            'in_favorites', 'license', 'price', 'tags',
            'extension', 'recommended',
        )

    def get_recommended(self, obj):
        """Getting a paginated list of recommendations based on most popular
        combo of tags and returns the [offset:limit] number of images
        """

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
            ).distinct()
            images = images | new_images

        limit = self.context['request'].query_params.get(
            'limit', IMAGES_RECOMENDED_SIZE
        )
        offset = self.context['request'].query_params.get(
            'offset', 0
        )
        images = images[int(offset):int(limit)]
        serializer = ImageShortSerializer(
            images, many=True, context=self.context
        )
        return serializer.data

    def get_in_favorites(self, obj):
        """Getting the number of times an image has been added to favorites.
        """

        return FavoriteImage.objects.filter(image__id=obj.id).count()

    def get_extension(self, obj):
        """Getting the extension of image."""

        return obj.image.name.split('.')[-1].upper()


class ImagePostPutPatchSerializer(serializers.ModelSerializer):
    """Image model serializer for post, put, patch requests."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Image
        fields = ('name', 'image', 'license', 'price', 'tags', )
        read_only_fields = ('role', )

    def to_representation(self, instance):
        serializer = ImageGetSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        """Modified object creation method that gets file extension
        information and creates entries in the TagImage table."""

        tags = validated_data.pop('tags')
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


class FavoriteSerialiser(serializers.ModelSerializer):
    """FavoriteImage model serializer for adding and deleting favorites."""

    class Meta:
        model = FavoriteImage
        fields = (
            'image',
            'user',
        )

    def validate(sels, data):
        image = data.get('image')
        user = data.get('user')
        if image.favoriteimage_set.filter(user=user).exists():
            raise ValidationError(
                detail={'errors': _('This image is already in favorites.')},
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for transferring and modifying user information."""

    favoriteds = serializers.SerializerMethodField(read_only=True)
    my_images = serializers.SerializerMethodField()
    count_my_images = serializers.SerializerMethodField(read_only=True)
    my_subscribers = serializers.SerializerMethodField(read_only=True)
    my_subscriptions = serializers.SerializerMethodField(read_only=True)
    history = serializers.SerializerMethodField(read_only=True)

    def get_my_images(self, obj):
        if (self.context.get('request')
           and self.context.get('request').user.is_authenticated and
                obj.role == 'Author'):
            limit = self.context.get('request').query_params.get(
                'limit', IMAGES_LIMIT_SIZE
            )
            images = obj.images.filter(author=obj.id)[:int(limit)]
            serializer = ImageShortSerializer(
                images, many=True, context=self.context
            )
            return serializer.data

    def get_history(self, obj):
        if (self.context.get('request')
           and self.context.get('request').user.is_authenticated):
            limit = self.context.get('request').query_params.get(
                'limit', IMAGES_LIMIT_SIZE
            )
            images = Image.objects.all()[:int(limit)]
            serializer = ImageShortSerializer(
                images, many=True, context=self.context
            )
            return serializer.data

    def get_favoriteds(self, obj):
        limit = self.context.get('request').query_params.get(
                'limit', IMAGES_LIMIT_SIZE
            )
        favorite_images = FavoriteImage.objects.filter(
            user=obj.id)[:int(limit)]
        images = [favorite_image.image for favorite_image in favorite_images]
        serializer = ImageShortSerializer(
            images, many=True, context=self.context
        )
        return serializer.data

    def get_count_my_images(self, obj):
        if (obj.role == 'Author'):
            images = obj.images.all()
            serializer = ImageShortSerializer(
                images, many=True, context=self.context
            )
            return len(serializer.data)

    def get_my_subscribers(self, obj):
        if (obj.role == 'Author'):
            queryset = Subscription.objects.filter(author=obj.id)
            serializer = MySubscribers(queryset, many=True)
            return len(serializer.data)

    def get_my_subscriptions(self, obj):
        queryset = Subscription.objects.filter(subscriber=obj.id)
        serializer = MySubscribers(queryset, many=True)
        return len(serializer.data)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'vk', 'instagram', 'website', 'profile_photo',
                  'birthday', 'my_images',
                  'role', 'favoriteds',
                  'count_my_images', 'my_subscribers',
                  'my_subscriptions', 'history',
                  )


class MySubscribers(serializers.ModelSerializer):
    """Serializer for Subscription model."""

    class Meta:
        model = Subscription
        fields = '__all__'
