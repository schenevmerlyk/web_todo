import json
from channels.generic.websocket import AsyncWebsocketConsumer

online_users = set()
user_channels = {}  # user_id -> channel_name

class DataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if self.user and not self.user.is_anonymous:
            self.user_id = self.user.id
            online_users.add(self.user_id)
            user_channels[self.user_id] = self.channel_name
            # Підписка на групу оновлень ToDo
            await self.channel_layer.group_add('todo_updates', self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Підключено до real-time сервера'
            }))
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_id'):
            online_users.discard(self.user_id)
            if self.user_id in user_channels:
                del user_channels[self.user_id]
            await self.channel_layer.group_discard('todo_updates', self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            to_user_id = data.get('to_user_id')
            payload = data.get('data', {})
            if to_user_id and to_user_id in online_users:
                target_channel = user_channels.get(to_user_id)
                if target_channel:
                    await self.channel_layer.send(
                        target_channel,
                        {
                            'type': 'send_data',
                            'from_user_id': self.user_id,
                            'data': payload
                        }
                    )
                    await self.send(text_data=json.dumps({'status': 'sent', 'to_user': to_user_id}))
                else:
                    await self.send(text_data=json.dumps({'error': 'Канал отримувача не знайдено'}))
            else:
                await self.send(text_data=json.dumps({'error': 'Користувач не в мережі або не існує'}))
        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def send_data(self, event):
        """Отримання даних від іншого користувача"""
        await self.send(text_data=json.dumps({
            'type': 'data_from_user',
            'from_user_id': event['from_user_id'],
            'data': event['data']
        }))

    async def send_todo_update(self, event):
        """Оновлення ToDo (від сигналів)"""
        await self.send(text_data=json.dumps({
            'type': 'todo_update',
            'action': event['action'],
            'todo': event['todo']
        }))