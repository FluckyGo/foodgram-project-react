from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.serializers import CustomUserReadSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор тега. """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор ингридиентов. """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ''' Сериализатор для модели Рецепт-Ингредиент. '''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserReadSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return bool(
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        return bool(
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(recipe=obj).exists())


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = AddRecipeIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def validate(self, data):
        cooking_time = data.get('cooking_time')
        image = data.get('image')

        if cooking_time is not None and cooking_time < 1:
            raise serializers.ValidationError(
                'Время готовки должно быть больше или равно 1.')

        if not image:
            raise serializers.ValidationError(
                'Проблема с картинкой, выбирите другую.'
            )

        return data

    def validate_tags(self, value):
        tags = value

        if not tags:
            raise exceptions.ValidationError('Тэг не выбран.')

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Тэги не должны повторяться.')

        return value

    def validate_ingredients(self, value):
        ingredients = value

        if not ingredients:
            raise exceptions.ValidationError('Ингредиенты не выбраны.')

        unique_ingredient_ids = set()

        for data in ingredients:
            ingredient_id = data.get('id')

            if int(data['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше 0.')

            if ingredient_id in unique_ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            else:
                unique_ingredient_ids.add(ingredient_id)

        return value

    def create(self, validated_data):

        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )

        recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        if not ingredients_data:
            raise serializers.ValidationError(
                'Поле ingredients обязательно при обновлении рецепта.')

        if not tags_data:
            raise serializers.ValidationError(
                'Поле tags обязательно при обновлении рецепта.')

        instance.ingredients.clear()
        instance.tags.clear()

        instance = super().update(instance, validated_data)

        for ingredient in ingredients_data:
            RecipeIngredient.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )

        instance.tags.set(tags_data)

        return instance

    def to_representation(self, instance):
        representation = RecipeReadSerializer(instance).data
        return representation


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
