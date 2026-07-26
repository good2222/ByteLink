from django.urls import path
from .views import (
    GroupListView,
    GroupCreateView,
    GroupDetailView,
    GroupJoinToggleView,
    GroupEditView,
    GroupDeleteView,
)

urlpatterns = [
    path('groups/', GroupListView.as_view(), name='group_list'),
    path('groups/create/', GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/join/', GroupJoinToggleView.as_view(), name='group_join'),
    path('groups/<int:pk>/edit/', GroupEditView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='group_delete'),
]
