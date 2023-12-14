
from rest_framework import serializers, validators
from django.contrib.auth import get_user_model
from .models import Follow
from recipes.models import Recipe
from api.serializers import RecipeFollowSerializer

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
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

    def validate(self, data):

        if data['user'] == data['following']:
            raise serializers.ValidationError(
                "Ты не можешь подписаться на самого себя."
            )
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, following=obj.following).exists()
        return False

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.following)
        serializer = RecipeFollowSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()
