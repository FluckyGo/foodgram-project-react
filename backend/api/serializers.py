
import base64
from rest_framework import serializers, status, validators
from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from recipes.models import (Tag, Ingredient, Recipe,
                            RecipeIngredient, Favorite, ShoppingCart)
from users.serializers import CustomUserReadSerializer

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
        read_only_fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ''' Сериализатор для модели Рецепт-Ингредиент. '''
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserReadSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=obj).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def create(self, validated_data):

        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                ingredient=ingredient['ingredient'], recipe=recipe)

        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class RecipeFollowSerializer(serializers.ModelSerializer):
    ''' Сериализатор модели рецепта при выводе подписок. '''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
