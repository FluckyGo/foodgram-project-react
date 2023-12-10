from rest_framework import serializers
from .models import CustomUser

USERNAME_REGEX = r'^[\w.@+-]+\z'


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False
