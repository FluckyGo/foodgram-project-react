from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserChangeForm

admin.site.empty_value_display = '-пусто-'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Админ-зона пользователей Django"""
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'role', 'admin_status', 'is_active',)
    search_fields = ('username', 'email', 'is_active',)
    list_filter = ('username', 'email', 'is_active',)
    list_editable = ('is_active',)

    def admin_status(self, obj):
        return 'Админ' if obj.is_admin else 'Обычный юзер'
    admin_status.short_description = 'Статус пользователя'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets += (("Change Password", {"fields": ("password",)}),)
        return fieldsets
