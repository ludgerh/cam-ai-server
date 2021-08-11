# c_server/asgi.py
import os
from django.conf.urls import url
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "c_server.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
from channels.auth import AuthMiddlewareStack
import c_client.routing

application = ProtocolTypeRouter({
	'http': django_asgi_app,
	'websocket': AuthMiddlewareStack(
		URLRouter(
			c_client.routing.websocket_urlpatterns
		)
	),
})

