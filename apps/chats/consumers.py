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

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()

        if not message_text:
            return

        # Сохраняем сообщение в БД
        msg = await self.save_message(message_text)

        # 1. Рассылаем сообщение участникам открытого чата
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

        # 2. Отправляем всплывающее push-уведомление собеседнику(ам) на любой странице
        recipient_ids = await self.get_recipients_ids()
        for recipient_id in recipient_ids:
            await self.channel_layer.group_send(
                f'user_{recipient_id}',
                {
                    'type': 'new_message_notification',
                    'room_id': self.room_id,
                    'message': msg.content,
                    'sender_username': self.user.username,
                    'sender_avatar': self.user.get_avatar_url,
                    'created_at': msg.created_at.strftime('%H:%M'),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, message_text):
        room = ChatRoom.objects.get(id=self.room_id)
        return ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=message_text
        )

    @database_sync_to_async
    def get_recipients_ids(self):
        room = ChatRoom.objects.get(id=self.room_id)
        return list(room.participants.exclude(id=self.user.id).values_list('id', flat=True))