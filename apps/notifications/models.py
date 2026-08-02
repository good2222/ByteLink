from django.db import models
from django.conf import settings

NOTIFICATION_TYPES = (
    ('like',           'Лайк'),
    ('comment',        'Комментарий'),
    ('friend_request', 'Заявка в друзья'),
    ('friend_accept',  'Принятие заявки в друзья'),
    ('group_invite',   'Группа'),
)


class Notification(models.Model):
    NOTIFICATION_TYPES = NOTIFICATION_TYPES

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Получатель'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='Отправитель'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name='Тип уведомления'
    )
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Пост'
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Группа'
    )
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'Уведомление для {self.recipient.username}: {self.get_notification_type_display()}'

    @property
    def get_icon(self):
        icons = {
            'like': 'bi-heart-fill text-danger',
            'comment': 'bi-chat-dots-fill text-info',
            'friend_request': 'bi-person-plus-fill text-warning',
            'friend_accept': 'bi-person-check-fill text-success',
            'group_invite': 'bi-collection-fill text-primary',
        }
        return icons.get(self.notification_type, 'bi-bell-fill')

    @property
    def get_text(self):
        from django.utils.translation import get_language
        lang = get_language() or 'uk'
        if lang == 'ru':
            texts = {
                'like': 'оценил(а) вашу публикацию.',
                'comment': 'оставил(а) комментарий к вашей публикации.',
                'friend_request': 'отправил(а) вам заявку в друзья.',
                'friend_accept': 'принял(а) вашу заявку в друзья.',
                'group_invite': f'приглашает вас в группу "{self.group.title if self.group else ""}".',
            }
            return texts.get(self.notification_type, 'новое уведомление.')
        else:
            texts = {
                'like': 'вподобав(ла) вашу публікацію.',
                'comment': 'залишив(ла) коментар до вашої публікації.',
                'friend_request': 'надіслав(ла) вам заявку до друзів.',
                'friend_accept': 'прийняв(ла) вашу заявку до друзів.',
                'group_invite': f'запрошує вас до групи "{self.group.title if self.group else ""}".',
            }
            return texts.get(self.notification_type, 'нове сповіщення.')