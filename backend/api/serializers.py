from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import exceptions, serializers, validators
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import CustomUser, Follow
from .constants import DEFAULT_FOLLOW_RECIPE_LIMIT

User = get_user_model()


class CustomUserReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для чтения данных о пользователе из БД.  """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """ Фукция для проверки наличия подписок. """
        return bool(
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and Follow.objects.filter(
                user=self.context.get('request').user,
                following=obj)
            .exists())


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
            and Favorite.objects.filter(
                recipe=obj,
                customer=self.context.get('request').user).exists())

    def get_is_in_shopping_cart(self, obj):
        return bool(
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                recipe=obj,
                customer=self.context.get('request').user).exists())


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
        image = data.get('image')
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        if not image:
            raise serializers.ValidationError(
                'Проблема с картинкой, выбирите другую.'
            )

        if not tags:
            raise exceptions.ValidationError('Тэг не выбран.')
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Тэги не должны повторяться.')

        if not ingredients:
            raise serializers.ValidationError('Ингредиенты не выбраны.')

        unique_ingredient_ids = set()

        for ingredient_data in ingredients:
            ingredient_id = ingredient_data.get('id')

            if ingredient_id in unique_ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            else:
                unique_ingredient_ids.add(ingredient_id)

        return data

    def safe_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'],
            )
                for ingredient_data in ingredients_data
            ])

    def create(self, validated_data):

        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            self.safe_ingredients(recipe, ingredients_data)
            recipe.tags.set(tags_data)

        return recipe

    def update(self, instance, validated_data):

        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        with transaction.atomic():
            instance.ingredients.clear()
            instance.tags.clear()
            instance = super().update(instance, validated_data)
            self.safe_ingredients(instance, ingredients_data)
            instance.tags.set(tags_data)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data


class RecipeFollowSerializer(serializers.ModelSerializer):
    ''' Сериализатор модели рецепта при выводе подписок. '''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseFavoriteShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate_item_existence(self, model, data, error_message):
        request = self.context.get('request')

        item = Recipe.objects.filter(
            pk=data.get('recipe').id).first()

        cart_instance = model.objects.filter(
            recipe=item, customer=request.user).first()

        if cart_instance:
            raise serializers.ValidationError(error_message)
        return data


class FavoriteReadSerializer(BaseFavoriteShoppingCartSerializer):
    class Meta(BaseFavoriteShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartReadSerializer(BaseFavoriteShoppingCartSerializer):
    class Meta(BaseFavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart


class FollowReadSerializer(serializers.ModelSerializer):
    """ Сериализатор подписки. """
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

        validators = [
            validators.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return bool(
            user.is_authenticated
            and Follow.objects.filter(
                user=user,
                following=obj.following)
            .exists())

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', DEFAULT_FOLLOW_RECIPE_LIMIT)

        try:
            limit = int(limit)
            if limit <= 0:
                raise ValueError(
                    "Значение 'recipes_limit' должно быть больше нуля.")

        except ValueError as e:
            return f'Ошибка: {e}'

        recipes = Recipe.objects.filter(author=obj.following)[:limit]
        serializer = RecipeFollowSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()


class FavoriteSerializer(BaseFavoriteShoppingCartSerializer):

    class Meta:
        model = Favorite
        fields = ('customer', 'recipe')

    def validate(self, data):
        return self.validate_item_existence(
            Favorite,
            data,
            'Рецепт уже в избранном.')

    def to_representation(self, instance):
        return FavoriteReadSerializer(instance).data


class ShoppingCartSerializer(BaseFavoriteShoppingCartSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('customer', 'recipe')

    def validate(self, data):
        return self.validate_item_existence(
            ShoppingCart,
            data,
            'Рецепт уже в списке покупок.')

    def to_representation(self, instance):
        return ShoppingCartReadSerializer(instance).data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        request = self.context.get('request')

        following = User.objects.filter(
            pk=data.get('following').id).first()

        if following == request.user:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя.'
            )

        follow_instance = Follow.objects.filter(
            user=request.user, following=following).first()

        if follow_instance:
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.')

        return data

    def to_representation(self, instance):
        return FollowReadSerializer(instance, context=self.context).data
