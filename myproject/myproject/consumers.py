import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from users.models import User

# Словник для зберігання id онлайн-користувачів (або використовуйте Redis)
online_users = set()

class DataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
    print("=== WebSocket connect attempt ===")
    print("User from scope:", self.scope.get('user'))
        self.user = self.scope.get('user')
        if self.user and not self.user.is_anonymous:
            self.user_id = self.user.id
            self.group_name = f'user_{self.user_id}'
            # Додаємо до глобальної множини онлайн
            online_users.add(self.user_id)
            # Додаємо канал до групи користувача
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Підключено до real-time сервера'
            }))
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'user_id') and self.user_id in online_users:
            online_users.discard(self.user_id)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            to_user_id = data.get('to_user_id')
            payload = data.get('data', {})
            if to_user_id and to_user_id in online_users:
                # Надсилання повідомлення через channel_layer в групу отримувача
                await self.channel_layer.send(
                    f'user_{to_user_id}',
                    {
                        'type': 'send_data',
                        'from_user_id': self.user_id,
                        'data': payload
                    }
                )
                await self.send(text_data=json.dumps({
                    'status': 'sent',
                    'to_user': to_user_id
                }))
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Користувач не в мережі або не існує'
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def send_data(self, event):
        """Обробник, який викликається при отриманні повідомлення через channel_layer"""
        await self.send(text_data=json.dumps({
            'type': 'data_from_user',
            'from_user_id': event['from_user_id'],
            'data': event['data']
        }))