from django.contrib.auth.forms import UserChangeForm

from .models import CustomUser


class CustomUserChangeForm(UserChangeForm):
    """ Кастомная форма для изменения пользователя в админке. """
    class Meta:
        model = CustomUser
        fields = '__all__'
