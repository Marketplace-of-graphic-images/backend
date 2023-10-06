import random

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

users_pool = (
    'test_user1', 'test_user2', 'test_user3',
    'test_user4', 'test_user5'
)
users = (
    {
        'username': 'test_user1',
        'email': 'test_user1@pictura.ru',
        'password': 'test_user1',
        'role': 'Author',
    },
    {
        'username': 'test_user2',
        'email': 'test_user2@pictura.ru',
        'password': 'test_user2',
        'role': 'Author',
    },
    {
        'username': 'test_user3',
        'email': 'test_user3@pictura.ru',
        'password': 'test_user3',
        'role': 'Author',
    },
    {
        'username': 'test_user4',
        'email': 'test_user4@pictura.ru',
        'password': 'test_user4',
        'role': 'Author',
    },
    {
        'username': 'test_user5',
        'email': 'test_user5@pictura.ru',
        'password': 'test_user5',
        'role': 'Author',
    },
)


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
            try:
                new_user, created = User.objects.get_or_create(**user)
                if created:
                    new_user.set_password(user.get('password'))
                    new_user.save()
            except IntegrityError:
                pass

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
                format=name.split('.')[-1].upper(),
            )
            new_image.tags.set(tags)
            new_image.save()
            return new_image
        except IntegrityError:
            pass

    def search_params(
            self, max_tags_in_one_name: int, count_name: int) -> list:
        """
        Generate a list of search parameters.

        Returns:
            list: A list of search parameters.
        """
        name = tags.keys()
        params = []
        for i in range(2, max_tags_in_one_name):
            for _ in range(count_name):
                search_name = random.sample(name, i)
                params.append(' '.join(search_name))
        return params

    def handle(self, *args, **kwargs):

        self.create_tags()
        self.create_users()
        users = User.objects.filter(username__in=users_pool)
        search_params = self.search_params(7, 6)
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
        print('Done!')
