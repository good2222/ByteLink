import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f'user_{self.user.id}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def new_message_notification(self, event):
        await self.send(text_data=json.dumps(event))
