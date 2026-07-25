# ============================================================
# ФАЙЛ: apps/users/models.py
# Описание: Модель пользователя (таблица в базе данных)
# ============================================================

# Импортируем модуль models из Django — он содержит все типы полей для БД
from django.db import models

# AbstractUser — базовый класс Django-пользователя с полями:
# username, password, email, first_name, last_name, is_active, is_staff и т.д.
# Мы наследуемся от него, чтобы добавить свои поля, не переписывая всё с нуля
from django.contrib.auth.models import AbstractUser


# Объявляем нашу кастомную модель пользователя
# Наследуется от AbstractUser — значит имеет все стандартные поля Django-пользователя
class CustomUser(AbstractUser):

    # Список возможных ролей пользователя — это кортеж из пар (значение_в_бд, отображение)
    ROLE_CHOICES = (
        ('user', 'Пользователь'),    # Обычный пользователь сайта
        ('admin', 'Администратор'),  # Администратор с дополнительными правами
    )

    # Поле роли — текстовое поле с ограниченным набором значений (choices)
    # max_length=10 — максимальная длина строки в БД
    # choices=ROLE_CHOICES — выпадающий список в Django Admin
    # default='user' — по умолчанию все новые пользователи получают роль 'user'
    # verbose_name — человекочитаемое название поля в Django Admin
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='Роль')

    # Поле "О себе" — длинный текст (TextField)
    # max_length=500 — максимум 500 символов
    # blank=True — поле необязательно для заполнения (можно оставить пустым)
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')

    # Статус пользователя — короткая фраза, как в ВК
    # CharField — обычная строка, не очень длинная
    # max_length=150 — максимум 150 символов
    status_message = models.CharField(max_length=150, blank=True, verbose_name='Статус')

    # Поле аватара — хранит путь к файлу изображения
    # upload_to='avatars/' — загруженные аватарки сохраняются в папку media/avatars/
    # default='avatars/default.png' — если аватарка не загружена, показывается дефолтная
    # blank=True — поле необязательно при создании через форму
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, verbose_name='Аватар')

    # Обложка профиля (как шапка профиля в Facebook/ВК)
    # upload_to='covers/' — файлы сохраняются в media/covers/
    cover_image = models.ImageField(upload_to='covers/', default='covers/default.png', blank=True, verbose_name='Обложка профиля')

    # Дата рождения — поле типа DATE (только дата, без времени)
    # null=True — разрешает хранить NULL в базе данных (поле не заполнено)
    # blank=True — разрешает пустое значение в форме
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')

    # Местоположение — город, страна
    # CharField т.к. короткий текст (до 100 символов)
    location = models.CharField(max_length=100, blank=True, verbose_name='Местоположение')

    # Ссылка на личный сайт
    # URLField — специальный тип, Django автоматически проверяет что это валидный URL
    website = models.URLField(max_length=200, blank=True, verbose_name='Сайт')

    # Мета-информация о модели (не поля, а настройки)
    class Meta:
        # Название модели в единственном числе (для Django Admin)
        verbose_name = 'Пользователь'
        # Название модели во множественном числе (для Django Admin)
        verbose_name_plural = 'Пользователи'

    # @property — делает метод доступным как атрибут: user.is_site_admin (без скобок)
    # Проверяет, является ли пользователь администратором сайта
    @property
    def is_site_admin(self):
        # Возвращает True если роль 'admin' ИЛИ если пользователь superuser (через manage.py createsuperuser)
        return self.role == 'admin' or self.is_superuser

    # Возвращает URL аватарки пользователя
    # Если аватарка есть и файл существует — возвращает её URL
    # Если нет — возвращает путь к дефолтному изображению
    @property
    def get_avatar_url(self):
        # Проверяем: есть ли поле avatar и есть ли у него атрибут url (значит файл назначен)
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                # Проверяем что файл физически существует на диске
                if self.avatar.storage.exists(self.avatar.name):
                    # Возвращаем URL вида /media/avatars/filename.png
                    return self.avatar.url
            except Exception:
                # Если что-то пошло не так — просто идём дальше и вернём дефолт
                pass
        # Импортируем функцию static — она строит URL к файлу в папке /static/
        from django.templatetags.static import static
        # Возвращаем URL к дефолтному аватару из папки static/images/
        return static('images/default-avatar.png')

    # Аналогично get_avatar_url, но для обложки профиля
    @property
    def get_cover_url(self):
        # Проверяем наличие поля cover_image и физического файла
        if self.cover_image and hasattr(self.cover_image, 'url'):
            try:
                if self.cover_image.storage.exists(self.cover_image.name):
                    # Возвращаем URL обложки из папки media/covers/
                    return self.cover_image.url
            except Exception:
                pass
        from django.templatetags.static import static
        # Возвращаем дефолтную обложку из папки static/images/
        return static('images/default-cover.png')

    # __str__ — определяет, как объект отображается в виде строки
    # Используется в Django Admin, логах и print()
    def __str__(self):
        # Показываем имя пользователя — например "egor"
        return self.username
