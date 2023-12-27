from api.serializers import RecipeFollowSerializer
from django.contrib.auth import get_user_model
from recipes.models import Recipe
from rest_framework import serializers, validators

from .models import Follow

User = get_user_model()

DEFAULT_LIMIT = 4


class FollowSerializer(serializers.ModelSerializer):
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
        if not user.is_anonymous:
            return Follow.objects.filter(
                user=user,
                following=obj.following).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', DEFAULT_LIMIT)
        recipes = Recipe.objects.filter(author=obj.following)[:int(limit)]
        serializer = RecipeFollowSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()
