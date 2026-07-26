# ============================================================
# ФАЙЛ: apps/groups/urls.py
# Маршруты (URL-адреса) для работы с группами (сообществами)
# ============================================================

from django.urls import path
from .views import (
    GroupListView,        # Каталог групп
    GroupCreateView,      # Создание группы
    GroupDetailView,      # Страница группы
    GroupJoinToggleView,  # Вступить / Выйти из группы
    GroupEditView,        # Редактирование настроек группы
    GroupDeleteView,      # Удаление группы
)

urlpatterns = [
    # URL: /groups/ — Каталог всех групп с поиском
    path('groups/', GroupListView.as_view(), name='group_list'),

    # URL: /groups/create/ — Страница создания нового сообщества
    path('groups/create/', GroupCreateView.as_view(), name='group_create'),

    # URL: /groups/5/ — Просмотр конкретной группы с ID=5
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group_detail'),

    # URL: /groups/5/join/ — Кнопка вступления / выхода из группы
    path('groups/<int:pk>/join/', GroupJoinToggleView.as_view(), name='group_join'),

    # URL: /groups/5/edit/ — Страница редактирования настроек группы
    path('groups/<int:pk>/edit/', GroupEditView.as_view(), name='group_edit'),

    # URL: /groups/5/delete/ — Удаление группы
    path('groups/<int:pk>/delete/', GroupDeleteView.as_view(), name='group_delete'),
]
