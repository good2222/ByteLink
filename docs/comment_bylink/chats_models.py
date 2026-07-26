# ============================================================
# ФАЙЛ: apps/chats/models.py
# Описание: Модели Комнаты чата и Сообщений
# ============================================================

from django.db import models
from django.conf import settings


# ============================================================
# МОДЕЛЬ: ChatRoom (Диалог / Комната чата)
# ============================================================
class ChatRoom(models.Model):

    # Участники переписки (двое пользователей)
    # ManyToManyField — связь "многие со многими"
    # related_name='chat_rooms' — доступ: user.chat_rooms.all() (все диалоги пользователя)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')

    # Дата и время создания диалога
    created_at = models.DateTimeField(auto_now_add=True)

    # Метод: возвращает вашего собеседника в этом диалоге
    def get_other_user(self, user):
        # Исключаем текущего пользователя и берем первого оставшегося
        return self.participants.exclude(id=user.id).first()

    # Метод: возвращает самое свежее сообщение из этой комнаты
    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def __str__(self):
        return f"Чат #{self.id}"


# ============================================================
# МОДЕЛЬ: ChatMessage (Одно личное сообщение)
# ============================================================
class ChatMessage(models.Model):

    # Ссылка на комнату чата, к которой относится сообщение
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')

    # Автор сообщения (отправитель)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')

    # Сам текст сообщения
    content = models.TextField()

    # Флаг прочитано ли сообщение
    is_read = models.BooleanField(default=False)

    # Точная дата и время отправки
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Порядок сообщений: от старых к новым (хронологический)
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
