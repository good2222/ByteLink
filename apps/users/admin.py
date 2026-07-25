from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FriendRequest

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_superuser']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'bio', 'status_message', 'avatar', 'cover_image', 'birth_date', 'location', 'website')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'email')
        }),
    )

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['from_user__username', 'to_user__username']

admin.site.register(CustomUser, CustomUserAdmin)
