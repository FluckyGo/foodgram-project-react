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

    class Meta:
        verbose_name = 'Подписчика'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        follower_user = User.objects.only('username').get(pk=self.user_id)
        followed_user = User.objects.only('username').get(pk=self.following_id)
        return f'{follower_user} подписан на {followed_user}'
