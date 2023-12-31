from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    """ Фильтр рецептов. """
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorite__customer=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shoppingcart__customer=user)
        return queryset


class IngredientFilter(rest_filters.SearchFilter):
    """ Фильтр для поиска ингридиентов. """
    search_param = 'name'
