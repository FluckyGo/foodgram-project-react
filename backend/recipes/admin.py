from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)

admin.site.empty_value_display = '-пусто-'


class TagResource(resources.ModelResource):
    """ Ресурс для экспорта и импорта тегов. """
    class Meta:
        model = Tag


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    """ Админ-зона тегов. """
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


class IngredientResource(resources.ModelResource):
    """Ресурс для экспорта и импорта ингридиентов."""
    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Админ-зона для модели Ingredient."""
    resource_classes = [IngredientResource]
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_display_links = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 3
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ''' Админ-зона рецептов. '''
    list_display = ('name', 'author', 'cooking_time',
                    'tags_list', 'ingredients_list', 'pub_date')
    search_fields = ('name', 'author', 'tags__name')
    list_filter = ('name', 'author', 'cooking_time', 'tags')
    filter_horizontal = ('ingredients',)
    inlines = (
        RecipeIngredientInline,
    )

    def tags_list(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])
    tags_list.short_description = 'Тэги'

    def ingredients_list(self, obj):
        return ', '.join(
            [ingredients.name for ingredients in obj.ingredients.all()]
        )
    ingredients_list.short_description = 'Ингридиенты блюда'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    ''' Админ-зона ингридиентов используемых в блюдах.  '''
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name__icontains',)
    list_filter = ('recipe', 'ingredient')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    ''' Админ-зона карточки с покупками.  '''
    list_display = ('customer', 'recipe')
    search_fields = ('customer', 'recipe')
    list_filter = ('customer', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    ''' Админ-зона любымых рецептов. '''
    list_display = ('customer', 'recipe')
    search_fields = ('customer', 'recipe')
    list_filter = ('customer', 'recipe')
