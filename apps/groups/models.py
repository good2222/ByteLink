from django.db import models
from django.conf import settings


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    description = models.TextField(verbose_name='Описание группы')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name='Создатель'
    )
    avatar = models.ImageField(upload_to='groups/avatars/', blank=True, null=True, verbose_name='Аватар группы')
    cover_image = models.ImageField(upload_to='groups/covers/', blank=True, null=True, verbose_name='Обложка группы')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def members_count(self):
        return self.memberships.count()

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


class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Участник'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')
        verbose_name = 'Участник группы'
        verbose_name_plural = 'Участники групп'

    def __str__(self):
        return f'{self.user.username} в {self.group.title} ({self.get_role_display()})'