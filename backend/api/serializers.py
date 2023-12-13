
from rest_framework import serializers, status, validators
from rest_framework.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from recipes.models import (Tag, Ingredient, Recipe,
                            RecipeIngredient, Favorite, ShoppingCart)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор тега. """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор ингридиентов. """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('author')
