from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    )
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='user',
        verbose_name='Роль'
    )
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name='О себе'
    )
    status_message = models.CharField(
        max_length=150, 
        blank=True, 
        verbose_name='Статус'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        default='avatars/default.png', 
        blank=True, 
        verbose_name='Аватар'
    )
    cover_image = models.ImageField(
        upload_to='covers/', 
        default='covers/default.png', 
        blank=True, 
        verbose_name='Обложка профиля'
    )
    birth_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Дата рождения'
    )
    location = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='Местоположение'
    )
    website = models.URLField(
        max_length=200, 
        blank=True, 
        verbose_name='Сайт'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_site_admin(self):
        return self.role == 'admin' or self.is_superuser

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

    def __str__(self):
        return self.username
