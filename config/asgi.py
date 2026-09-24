import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)


from django.core.asgi import (
    get_asgi_application
)

from channels.routing import (
    ProtocolTypeRouter,
    URLRouter
)

from camera.routing import (
    websocket_urlpatterns
)


django_application = (
    get_asgi_application()
)


application = ProtocolTypeRouter({

    "http":
        django_application,

    "websocket":
        URLRouter(
            websocket_urlpatterns
        ),
})