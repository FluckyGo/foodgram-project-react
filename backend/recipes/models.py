from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """ Модель тегов. """
    ORANGE = '#FFA500'
    AQUA = '#00FFFF'
    INDIGO = '#4B0082'

    COLOR_SET = [
        (ORANGE, 'Оранжевый'),
        (AQUA, 'Бирюзовый'),
        (INDIGO, 'Синий'),
    ]

    name = models.CharField('Наименование тега', max_length=200, unique=True)
    color = models.CharField('Цвет тега', max_length=7,
                             choices=COLOR_SET, default=ORANGE, unique=True)
    slug = models.SlugField('Слаг тега', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингридиентов. """
    name = models.CharField(
        'Название ингридиента',
        max_length=150,
        db_index=True
    )

    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    """ Модель рецептов. """
    ...


class Follow(models.Model):
    """ Модель подписок. """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Подписан'
    )

    def __str__(self):
        return f'{self.user.username} подписан на {self.following.username}'

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
