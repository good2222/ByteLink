# ============================================================
# ФАЙЛ: apps/posts/urls.py
# Маршруты (URL-адреса) для работы с публикациями
# ============================================================

# Импортируем функцию path — она связывает URL-адрес с нужным обработчиком (view)
from django.urls import path

# Импортируем все view-классы из posts/views.py
# Каждый класс отвечает за одно конкретное действие
from .views import (
    PostCreateView,       # Создание нового поста
    PostDeleteView,       # Удаление поста
    LikeToggleView,       # Поставить / снять лайк
    CommentCreateView,    # Добавить комментарий
    CommentDeleteView,    # Удалить комментарий
)

# Список всех URL-маршрутов для приложения posts
urlpatterns = [

    # URL: /post/create/
    # Когда пользователь отправляет форму создания поста — вызывается PostCreateView
    # name='post_create' — это имя маршрута, используется в шаблонах через {% url 'post_create' %}
    path('post/create/', PostCreateView.as_view(), name='post_create'),

    # URL: /post/5/delete/ (где 5 — ID поста)
    # <int:pk> — переменная в URL, Django автоматически передаёт её во view как pk (primary key)
    # Вызывает PostDeleteView, который удаляет пост с указанным ID
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),

    # URL: /post/5/like/
    # Вызывает LikeToggleView — если лайк уже есть, снимает его; если нет — ставит
    # Работает только через POST-запрос (HTML форма с CSRF токеном)
    path('post/<int:pk>/like/', LikeToggleView.as_view(), name='post_like'),

    # URL: /post/5/comment/
    # Вызывает CommentCreateView — добавляет новый комментарий к посту с ID=pk
    path('post/<int:pk>/comment/', CommentCreateView.as_view(), name='comment_create'),

    # URL: /comment/12/delete/ (где 12 — ID комментария)
    # Вызывает CommentDeleteView — удаляет комментарий
    # Доступно только автору комментария, автору поста или администратору
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]
