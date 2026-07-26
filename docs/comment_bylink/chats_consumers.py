# ============================================================
# ФАЙЛ: apps/chats/consumers.py
# Обработчик WebSockets (сообщения в реальном времени)
# ============================================================

import json

# AsyncWebsocketConsumer — асинхронный базовый класс для работы с вебсокетами в Django Channels
from channels.generic.websocket import AsyncWebsocketConsumer

# database_sync_to_async — позволяет безопасно обращаться к базе данных из асинхронного кода
from channels.db import database_sync_to_async

from .models import ChatRoom, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):

    # 1. Вызывается при открытии браузером WebSocket соединения
    async def connect(self):
        # Получаем ID комнаты из URL: /ws/chat/5/ -> room_id = 5
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        # Формируем имя группы в памяти: "chat_5"
        self.room_group_name = f'chat_{self.room_id}'
        # Текущий авторизованный пользователь
        self.user = self.scope['user']

        # Если не авторизован — закрываем соединение
        if not self.user.is_authenticated:
            await self.close()
            return

        # Подключаем соединение к единой группе комнаты в памяти
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Подтверждаем установку соединения
        await self.accept()

    # 2. Вызывается при закрытии вкладки или соединении
    async def disconnect(self, close_code):
        # Удаляем соединение из группы комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 3. Вызывается когда пользователь присылает сообщение из браузера
    async def receive(self, text_data):
        # Разбираем пришедшую JSON-строку
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()

        if not message_text:
            return

        # Асинхронно сохраняем сообщение в базу данных
        msg = await self.save_message(message_text)

        # Рассылаем собранное сообщение ВСЕМ подключенным пользователям комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message', # Вызывает метод chat_message ниже
                'message_id': msg.id,
                'message': msg.content,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'sender_avatar': self.user.get_avatar_url,
                'created_at': msg.created_at.strftime('%H:%M'),
            }
        )

    # 4. Вызывается для каждого клиента в группе при получении сообщения от сервера
    async def chat_message(self, event):
        # Отправляем JSON обратно в браузер пользователя по открытому вебсокету
        await self.send(text_data=json.dumps(event))

    # Вспомогательный метод сохранения в БД (работает с синхронной ORM асинхронно)
    @database_sync_to_async
    def save_message(self, message_text):
        room = ChatRoom.objects.get(id=self.room_id)
        return ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=message_text
        )
