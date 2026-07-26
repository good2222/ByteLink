import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Разрешаем подключение только авторизованным пользователям
        if not self.user.is_authenticated:
            await self.close()
            return

        # Добавляем соединение в группу в памяти
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Удаляем соединение из группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()

        if not message_text:
            return

        # Сохраняем сообщение в базу данных асинхронно
        msg = await self.save_message(message_text)

        # Рассылаем собранное сообщение всем в комнате
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': msg.id,
                'message': msg.content,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'sender_avatar': self.user.get_avatar_url,
                'created_at': msg.created_at.strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        # Отправляем JSON обратно в браузер через открытый WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, message_text):
        room = ChatRoom.objects.get(id=self.room_id)
        return ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=message_text
        )