from django.contrib import admin
from .models import Group, GroupMembership


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'created_at', 'members_count']
    search_fields = ['title', 'description', 'creator__username']
    list_filter = ['created_at']


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['group__title', 'user__username']
