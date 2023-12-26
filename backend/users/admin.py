from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser

admin.site.empty_value_display = '-пусто-'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Админ-зона пользователей Django"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'role', 'admin_status', 'is_active',)
    search_fields = ('username', 'email', 'is_active',)
    list_filter = ('username', 'email', 'is_active',)
    list_editable = ('is_active',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'email',
                       'first_name', 'last_name', 'role'),
        }),
    )

    def admin_status(self, obj):
        return 'Админ' if obj.is_admin else 'Обычный юзер'
    admin_status.short_description = 'Статус пользователя'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets += (("Change Password", {"fields": ("password",)}),)
        return fieldsets
