from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from api.constants import (USERNAME_FIELD, REQUIRED_FIELDS,
                           MAX_USER_MODEL_FIELD_LENGTH)


class CustomUser(AbstractUser):
    """ Кастомная модель пользователя. """

    USERNAME_FIELD = USERNAME_FIELD
    REQUIRED_FIELDS = REQUIRED_FIELDS

    username = models.CharField(
        'Логин',
        max_length=MAX_USER_MODEL_FIELD_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )

    password = models.CharField(
        'Пароль', max_length=MAX_USER_MODEL_FIELD_LENGTH)

    email = models.EmailField(
        'E-mail адрес',
        unique=True
    )

    first_name = models.CharField(
        'Имя', max_length=MAX_USER_MODEL_FIELD_LENGTH)
    last_name = models.CharField(
        'Фамилия', max_length=MAX_USER_MODEL_FIELD_LENGTH)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    """ Модель подписок. """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Подписан'
    )

    class Meta:
        verbose_name = 'Подписчика'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
