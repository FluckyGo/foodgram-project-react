from django.contrib import admin
from .models import Ingredient, Tag

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
