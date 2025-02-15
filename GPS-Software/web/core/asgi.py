"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# Initialize Django ASGI application early to ensure the AppRegistry is populated
django_asgi_app = get_asgi_application()
# Set the default Django settings module
from api.routing import websocket_urlpatterns  # Import your WebSocket routes
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})