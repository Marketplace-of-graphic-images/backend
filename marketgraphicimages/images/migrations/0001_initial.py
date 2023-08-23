# Generated by Django 4.2 on 2023-08-14 07:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Любимое изображение',
                'verbose_name_plural': 'Любимые изображения',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Автоматически устанавливается текущая дата и время', verbose_name='Дата создания')),
                ('name', models.CharField(help_text='Введите название', max_length=200, unique=True, verbose_name='Название')),
                ('image', models.ImageField(help_text='Добавьте изображение', unique=True, upload_to='Images/', verbose_name='Картинка')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCartImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ForeignKey(help_text='Выберите изображения', on_delete=django.db.models.deletion.CASCADE, to='images.image', verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'Купленное изображение',
                'verbose_name_plural': 'Купленные изображения',
            },
        ),
    ]