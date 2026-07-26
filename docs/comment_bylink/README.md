# ============================================================
# ДОКУМЕНТАЦИЯ: ByteLink — Социальная сеть на Django
# Папка: docs/comment_bylink/
# ============================================================
#
# В этой папке находятся все файлы проекта с подробными
# комментариями к каждой строке кода.
#
# Цель: понять, как работает каждая часть сайта.
# ============================================================

"""
# СТРУКТУРА ПРОЕКТА ByteLink

ByteLink/
├── social_network/          ← Главный модуль Django-проекта
│   ├── settings.py          ← Все настройки проекта (БД, приложения, ключи)
│   ├── urls.py              ← Главный файл маршрутов (URL-адресов) сайта
│   ├── wsgi.py              ← Точка входа для обычного веб-сервера
│   └── asgi.py              ← Точка входа для асинхронного сервера (WebSockets)
│
├── apps/                    ← Все Django-приложения (модули) проекта
│   ├── users/               ← Приложение для пользователей и друзей
│   │   ├── models.py        ← Модели CustomUser и FriendRequest
│   │   ├── views.py         ← Обработчики профилей, друзей и поиска
│   │   ├── forms.py         ← Формы регистрации и редактирования профиля
│   │   └── urls.py          ← URL-маршруты для пользователей
│   │
│   ├── posts/               ← Приложение для публикаций
│   │   ├── models.py        ← Модели Post, Comment, Like
│   │   ├── views.py         ← Обработчики: создание/удаление постов, лайки
│   │   ├── forms.py         ← Формы создания поста и комментария
│   │   └── urls.py          ← URL-маршруты для постов
│   │
│   └── groups/              ← Приложение для групп (сообществ)
│       ├── models.py        ← Модели Group и GroupMembership
│       ├── views.py         ← Обработчики: каталог, создание, вступление
│       ├── forms.py         ← Форма создания/редактирования группы
│       └── urls.py          ← URL-маршруты для групп
│
├── templates/               ← HTML-шаблоны (внешний вид страниц)
│   ├── base.html            ← Базовый шаблон (шапка, навигация, футер)
│   ├── home.html            ← Главная страница (лента постов)
│   ├── registration/        ← Вход и регистрация
│   ├── users/               ← Страницы пользователей, друзей и поиска
│   └── groups/              ← Страницы групп (каталог, группа, создание)
│
└── docs/comment_bylink/     ← Документация (этот раздел)


# СПИСОК ФАЙЛОВ С КОММЕНТАРИЯМИ СТРОКА ЗА СТРОКОЙ

| Документ             | Исходный файл в проекте               | Описание
|----------------------|---------------------------------------|------------------------------
| settings.py          | social_network/settings.py            | Настройки Django-проекта
| urls_main.py         | social_network/urls.py                | Главные URL-маршруты
| urls_users.py        | apps/users/urls.py                    | URL-маршруты пользователей
| users_models.py      | apps/users/models.py                  | Модель CustomUser и FriendRequest
| users_views.py       | apps/users/views.py                   | View-классы пользователей и друзей
| users_forms.py       | apps/users/forms.py                   | Формы пользователей
| posts_models.py      | apps/posts/models.py                  | Модели Post, Comment, Like
| posts_views.py       | apps/posts/views.py                   | View-классы постов и лайков
| posts_forms.py       | apps/posts/forms.py                   | Формы постов
| posts_urls.py        | apps/posts/urls.py                    | URL-маршруты постов
| groups_models.py     | apps/groups/models.py                 | Модели Group и GroupMembership
| groups_views.py      | apps/groups/views.py                  | View-классы сообществ
| groups_urls.py       | apps/groups/urls.py                   | URL-маршруты групп
| README.md            | (этот файл)                           | Оглавление и структура
"""
