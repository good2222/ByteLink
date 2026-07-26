# ============================================================
# ФАЙЛ: apps/groups/models.py
# Описание: Модели Группы (сообщества) и Участников группы
# ============================================================

# Импортируем модуль models из Django — содержит типы полей для таблиц базы данных
from django.db import models

# settings — объект настроек Django, нужен для ссылки на модель пользователя (CustomUser)
from django.conf import settings


# ============================================================
# МОДЕЛЬ: Group (Группа / Сообщество)
# Каждая запись = отдельная группа в базе данных
# ============================================================
class Group(models.Model):

    # Название группы — текстовая строка длиной до 200 символов
    title = models.CharField(max_length=200, verbose_name='Название группы')

    # Описание группы — подробный многострочный текст
    description = models.TextField(verbose_name='Описание группы')

    # Создатель группы — ссылка на пользователя, который создал группу
    # on_delete=models.CASCADE — если пользователя удалят, его созданные группы тоже удалятся
    # related_name='created_groups' — доступ: user.created_groups.all() (все группы созданные пользователем)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name='Создатель'
    )

    # Аватарка группы — загружается в папку media/groups/avatars/
    # blank=True, null=True — изображение необязательно
    avatar = models.ImageField(upload_to='groups/avatars/', blank=True, null=True, verbose_name='Аватар группы')

    # Обложка группы (шапка) — загружается в папку media/groups/covers/
    cover_image = models.ImageField(upload_to='groups/covers/', blank=True, null=True, verbose_name='Обложка группы')

    # Дата и время создания группы — заполняется автоматически
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        # Сортировка по умолчанию: новые группы сверху
        ordering = ['-created_at']

    # Название группы при отображении в админке или в логах
    def __str__(self):
        return self.title

    # Свойство: количество участников в группе
    # self.memberships — все записи участников из таблицы GroupMembership
    # .count() — быстрый SQL-запрос количества строк
    @property
    def members_count(self):
        return self.memberships.count()

    # Свойство: возвращает URL аватарки группы или дефолтную картинку
    @property
    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                if self.avatar.storage.exists(self.avatar.name):
                    return self.avatar.url
            except Exception:
                pass
        from django.templatetags.static import static
        return static('images/default-avatar.png')

    # Свойство: возвращает URL обложки группы или дефолтную обложку
    @property
    def get_cover_url(self):
        if self.cover_image and hasattr(self.cover_image, 'url'):
            try:
                if self.cover_image.storage.exists(self.cover_image.name):
                    return self.cover_image.url
            except Exception:
                pass
        from django.templatetags.static import static
        return static('images/default-cover.png')


# ============================================================
# МОДЕЛЬ: GroupMembership (Участник группы)
# Связывает пользователя и группу, указывая роль
# ============================================================
class GroupMembership(models.Model):

    # Варианты ролей пользователя в группе
    ROLE_CHOICES = [
        ('member', 'Участник'),      # Обычный участник
        ('moderator', 'Модератор'),  # Модератор (может удалять посты)
        ('admin', 'Администратор'),  # Администратор группы (полный доступ)
    ]

    # Группа, в которой состоит пользователь
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')

    # Пользователь, состоящий в группе
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')

    # Роль пользователя в этой группе
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')

    # Дата вступления в группу
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Уникальность связки (group, user) — пользователь не может вступить в одну группу дважды
        unique_together = ('group', 'user')
        verbose_name = 'Участник группы'
        verbose_name_plural = 'Участники групп'

    def __str__(self):
        return f'{self.user.username} в {self.group.title} ({self.get_role_display()})'
