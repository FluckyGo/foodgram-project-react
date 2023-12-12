from django.contrib import admin
from .models import Follow, Ingredient, Tag

from import_export import resources
from import_export.admin import ImportExportModelAdmin


admin.site.empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Админка тегов. """
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


class IngredientResource(resources.ModelResource):
    """Ресурс для экспорта и импорта ингридиентов."""
    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Администратор для модели Ingredient."""
    resource_classes = [IngredientResource]
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_display_links = ('name',)


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
