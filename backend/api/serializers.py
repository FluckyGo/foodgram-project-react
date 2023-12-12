
from rest_framework import serializers, status, validators
from rest_framework.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from recipes.models import (Follow, Tag, Ingredient, Recipe,
                            RecipeIngredient, Favorite, ShoppingCart)

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор ингридиентов. """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор тега. """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('name', 'color', 'slug',)


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    def validate(self, data):

        if data['user'] == data['following']:
            raise serializers.ValidationError(
                "Ты не можешь подписаться на самого себя."
            )
        return data

    class Meta:
        model = Follow
        fields = ('user', 'following')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]
