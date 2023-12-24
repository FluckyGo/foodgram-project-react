from django.contrib import admin

from .models import Follow

admin.site.empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-зона подписчиков. """
    list_display = ('user', 'following',)
    search_fields = ('user__username', 'following__username',)
    list_filter = ('user__username', 'following__username',)

    def user(self, obj):
        return obj.user.username
    user.short_description = 'Пользователь'

    def following(self, obj):
        return obj.following.username
    following.short_description = 'Подписчик'
