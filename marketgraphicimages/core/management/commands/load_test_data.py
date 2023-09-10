import random

from comments.models import Comment
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.core.management import BaseCommand
from django.db.utils import IntegrityError
from tqdm import tqdm

from core.image_from_google import get_img_file, get_img_from_google
from images.models import Image
from tags.models import Tag

User = get_user_model()

tags = {
    'Природа': 'nature',
    'Путешествия': 'trevels',
    'Здоровье': 'health',
    'Город': 'city',
    'Искусство': 'art',
    'Еда': 'food',
    'Музыка': 'music',
    'Спорт': 'sport',
    'Развлечения': 'entertainment',
    'Портрет': 'portret',
}

users = (
    {
        'username': 'test_user1',
        'email': 'test_user1@pictura.ru',
        'password': 'test_user1',
        'author': True,
    },
    {
        'username': 'test_user2',
        'email': 'test_user2@pictura.ru',
        'password': 'test_user2',
        'author': True,
    },
    {
        'username': 'test_user3',
        'email': 'test_user3@pictura.ru',
        'password': 'test_user3',
        'author': True,
    },
)

comments_pool = [
    'Искусство на высшем уровне!',
    'Это действительно впечатляет.',
    'Очаровательное изображение!',
    'Ваш талант безграничен.',
    'Прекрасный момент!',
    'Это такое вдохновение!',
    'Удивительная работа!',
    'Великолепно!',
    'Очень креативно!',
    'Мне нравится ваш стиль!',
    'У вас невероятное чувство цвета.',
    'Просто потрясающе!',
    'Изумительная композиция.',
    'Отличная работа с контрастами!',
    'Каждая деталь на своем месте.',
    'С таким талантом далеко пойдете!',
    'Прекрасная работа!',
]


class Command(BaseCommand):

    def create_tags(self) -> None:
        """
        Creates tags.
        """
        for name, slug in tqdm(
            tags.items(), desc='Creating tags', colour='green'
        ):
            tag, created = Tag.objects.get_or_create(
                name=name,
                slug=slug,
            )
            if created:
                tag.save()

    def create_users(self) -> list:
        """
        Create users.
        """
        for user in tqdm(users, desc='Creating users', colour='green'):
            user, created = User.objects.get_or_create(**user)
            if created:
                user.save()

    def create_image(
            self,
            user: User,
            name: str,
            image: ImageFile,
            tags: Tag,
    ) -> None:
        """
        Create image.
        """
        try:
            new_image, _ = Image.objects.get_or_create(
                author=user,
                name=name,
                license='free',
                price=0,
                image=image,
            )
            new_image.tags.set(tags)
            new_image.save()
            return new_image
        except IntegrityError:
            pass

    def create_comment(self, images: Image, users: User) -> None:
        """
        Create comments.
        """
        for image in tqdm(images, desc='Creating comments', colour='green'):
            user = random.choice(users)
            comment, _ = Comment.objects.get_or_create(
                commented_post=image,
                commentator=user,
            )
            comment.text = random.choice(comments_pool)
            comment.save()

    def search_params(self) -> list:
        """
        Generate a list of search parameters.

        Returns:
            list: A list of search parameters.
        """
        name = tags.keys()
        params = []
        for i in range(2, 7):
            for _ in range(6):
                search_name = random.sample(name, i)
                params.append(' '.join(search_name))
        return params

    def handle(self, *args, **kwargs):

        self.create_tags()
        self.create_users()
        users = User.objects.all()
        search_params = self.search_params()
        created_img = []
        for search_name in tqdm(
            search_params, desc='Creating images', colour='green'
        ):
            tags = Tag.objects.filter(name__in=search_name.split())
            images = get_img_from_google(search_name=search_name, num_images=5)
            for image in images.results():
                image_file = get_img_file(image)
                image_model = self.create_image(
                    user=random.choice(users),
                    name=image.url,
                    image=image_file,
                    tags=tags,
                )
                created_img.append(image_model)
        self.create_comment(images=created_img, users=users)
        print('Done!')
