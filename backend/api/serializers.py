
from rest_framework import serializers, status, validators
from rest_framework.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from recipes.models import Follow

User = get_user_model()


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