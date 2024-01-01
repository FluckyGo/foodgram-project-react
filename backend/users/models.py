from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import USER, ADMIN, USER_ROLES


class CustomUser(AbstractUser):
    """ Кастомная модель пользователя. """
    admin = ADMIN

    username = models.CharField('Логин', max_length=150, unique=True)
    password = models.CharField('Пароль', max_length=150)
    email = models.EmailField('E-mail адрес', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
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
