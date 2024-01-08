from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, RegexValidator

from api.constants import (USER, ADMIN, USER_ROLES,
                           MAX_USER_MODEL_FIELD_LENGTH, USERNAME_REGEX)


class CustomUser(AbstractUser):
    """ Кастомная модель пользователя. """
    admin = ADMIN

    username = models.CharField(
        'Логин',
        max_length=MAX_USER_MODEL_FIELD_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message='Введите корретный юзернэйм.')
        ])

    password = models.CharField(
        'Пароль', max_length=MAX_USER_MODEL_FIELD_LENGTH)
    email = models.EmailField(
        'E-mail адрес',
        max_length=MAX_USER_MODEL_FIELD_LENGTH,
        unique=True,
        validators=[
            EmailValidator('Введите корректный адрес.')
        ])
    first_name = models.CharField(
        'Имя', max_length=MAX_USER_MODEL_FIELD_LENGTH)
    last_name = models.CharField(
        'Фамилия', max_length=MAX_USER_MODEL_FIELD_LENGTH)
    role = models.CharField(
        'Роль',
        max_length=50,
        choices=USER_ROLES,
        default=USER
    )
    is_active = models.BooleanField(
        verbose_name="Активeн",
        default=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name', ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.role == self.admin or self.is_staff


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
