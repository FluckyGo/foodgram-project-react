from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Follow

admin.site.empty_value_display = '-пусто-'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Админ-зона пользователей Django"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'admin_status', 'is_active',)
    search_fields = ('username', 'email', 'is_active',)
    list_filter = ('username', 'email', 'is_active',)
    list_editable = ('is_active',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'username',
                       'first_name', 'last_name'),
        }),
    )

    def admin_status(self, obj):
        return 'Админ' if obj.is_staff else 'Обычный юзер'
    admin_status.short_description = 'Статус пользователя'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets += (("Change Password", {"fields": ("password",)}),)
        return fieldsets


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-зона подписчиков. """
    list_display = ('user', 'following',)
    search_fields = ('user__username', 'following__username',)
    list_filter = ('user__username', 'following__username',)

    def user(self, obj):
        return obj.user.username
    user.short_description = 'Пользователь'

    def following(self, obj):
        return obj.following.username
    following.short_description = 'Подписчик'
