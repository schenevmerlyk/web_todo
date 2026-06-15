import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

http_application = get_asgi_application()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth.models import AnonymousUser
        from users.models import User

        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                user = await self.get_user(user_id)
                scope['user'] = user
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        from users.models import User
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()

# Лінива ініціалізація WebSocket маршрутів
_websocket_router = None

def get_websocket_router():
    global _websocket_router
    if _websocket_router is None:
        from channels.routing import URLRouter
        from realtime.routing import websocket_urlpatterns
        _websocket_router = TokenAuthMiddleware(URLRouter(websocket_urlpatterns))
    return _websocket_router

application = ProtocolTypeRouter({
    'http': http_application,
    'websocket': get_websocket_router(),
})