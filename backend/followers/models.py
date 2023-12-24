from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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
        verbose_name = 'Подписчика'
        verbose_name_plural = 'Подписчики'
