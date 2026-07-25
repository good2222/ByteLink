from django.contrib import admin
from .models import Post, Comment, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created_at', 'likes_count', 'comments_count')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__username')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
