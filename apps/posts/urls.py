from django.urls import path
from .views import (
    PostCreateView,
    PostDeleteView,
    LikeToggleView,
    CommentCreateView,
    CommentDeleteView,
)

urlpatterns = [
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/like/', LikeToggleView.as_view(), name='post_like'),
    path('post/<int:pk>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]
