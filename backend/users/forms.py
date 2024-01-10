from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserChangeForm(UserChangeForm):
    """ Кастомная форма для изменения пользователя в админке. """
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    """ Кастомная форма для создания пользователя в админке. """
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + \
            ('email', 'first_name', 'last_name')
