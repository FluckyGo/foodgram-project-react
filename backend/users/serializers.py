from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from recipes.models import Follow

USERNAME_REGEX = r'^[\w.@+-]+$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


class CustomUserReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для чтения данных о пользователе из БД.  """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """ Фукция для проверки наличия подписок. """
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False


class CustomUserWriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для записи данных о пользователе в БД.
    Регистрация пользователя.  """
    email = serializers.EmailField(
        required=True,
        validators=[RegexValidator(regex=EMAIL_REGEX,)]
    )
    username = serializers.CharField(
        required=True,
        validators=[RegexValidator(regex=USERNAME_REGEX,)]
    )
    first_name = serializers.CharField(required=True,)
    last_name = serializers.CharField(required=True,)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']

        existing_user_by_email = CustomUser.objects.filter(email=email).first()
        existing_user_by_username = CustomUser.objects.filter(
            username=username).first()

        if existing_user_by_email:
            raise ValidationError(
                'Пользователь с таким адресом почты уже существует!',
                code=status.HTTP_400_BAD_REQUEST)

        if existing_user_by_username:
            raise ValidationError(
                'Пользователь с таким ником существует!',
                code=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create(**validated_data)
        user.password = make_password(validated_data['password'])
        user.save()
        return user
