# =====================================================================
# ФАЙЛ: apps/notifications/consumers.py
# ЩО РОБИТЬ ЦЕЙ ФАЙЛ:
#   Цей файл — "вуха" кожного користувача.
#   Коли хтось надсилає тобі повідомлення в чаті — цей Consumer
#   перехоплює сигнал і надсилає спалах-повідомлення (push-notification)
#   прямо в браузер користувача БЕЗ перезавантаження сторінки.
# =====================================================================

import json
# AsyncWebsocketConsumer — асинхронний клас Django Channels для роботи з WebSockets.
# Async (асинхронний) означає: Django не чекає відповіді, а одразу обробляє
# наступні запити. Це дозволяє утримувати тисячі відкритих з'єднань одночасно.
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Персональний WebSocket-consumer для кожного авторизованого користувача.

    Коли браузер відкриває сторінку будь-якого розділу сайту,
    JavaScript підключається до /ws/notifications/ і залишається
    там на постійному "прослуховуванні". Якщо сервер надсилає
    сигнал — браузер миттєво його отримає та покаже повідомлення.
    """

    async def connect(self):
        """
        Метод викликається ОДИН РАЗ, коли браузер відкриває WebSocket з'єднання.
        Тут ми:
        1. Перевіряємо, чи користувач авторизований.
        2. Прив'язуємо це з'єднання до унікальної групи користувача в пам'яті.
        3. Підтверджуємо з'єднання (accept).
        """
        # self.scope — словник з інформацією про з'єднання (схожий на request в Django).
        # scope['user'] — поточний авторизований користувач (або AnonymousUser).
        self.user = self.scope['user']

        # Якщо користувач не авторизований — закриваємо з'єднання відразу.
        # Це захист: анонімний відвідувач не повинен отримувати нічиї повідомлення.
        if not self.user.is_authenticated:
            await self.close()
            return

        # Формуємо унікальне ім'я групи для цього користувача.
        # Наприклад: 'user_5', 'user_42', 'user_100'.
        # self.channel_layer — це сховище в пам'яті сервера (InMemoryChannelLayer).
        # Через нього ChatConsumer буде надсилати сигнал саме у цю групу.
        self.user_group_name = f'user_{self.user.id}'

        # Підключаємо поточне WebSocket-з'єднання до групи цього користувача.
        # channel_layer.group_add(назва_групи, ім'я_поточного_каналу)
        # self.channel_name — унікальний ідентифікатор ЦЬОГО конкретного з'єднання.
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Підтверджуємо з'єднання з боку сервера — браузер "знає" що підключений.
        await self.accept()

    async def disconnect(self, close_code):
        """
        Метод викликається коли браузер закриває вкладку або z'єднання.
        close_code — числовий код причини закриття (наприклад 1000 = нормально).
        Тут ми прибираємо з'єднання з групи, щоб не накопичувати мертві канали.
        """
        if self.user.is_authenticated:
            # Видаляємо це з'єднання з групи користувача.
            # Якщо користувач відкрив кілька вкладок — видаляємо тільки одну.
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def new_message_notification(self, event):
        """
        Цей метод викликається коли ChatConsumer надсилає сигнал у групу 'user_X'.
        Параметр event — словник з даними:
            {
                'type': 'new_message_notification',
                'room_id': 5,
                'message': 'Привіт!',
                'sender_username': 'alice',
                'sender_avatar': '/media/avatars/alice.jpg',
                'created_at': '14:35',
            }
        Метод просто пересилає ці дані через WebSocket у браузер користувача.
        Там їх перехоплює наш JavaScript в base.html і показує красивий тост.
        """
        # json.dumps() перетворює Python-словник у JSON-рядок.
        # self.send() надсилає цей рядок через відкритий WebSocket у браузер.
        await self.send(text_data=json.dumps(event))
