from django.urls import re_path

from .consumers import (
    CameraUploadConsumer,
    CameraViewerConsumer,
)


websocket_urlpatterns = [

    # ESP32 → Django
    re_path(
        r"ws/camera/"
        r"(?P<camera_id>[^/]+)/"
        r"upload/$",

        CameraUploadConsumer.as_asgi(),
    ),

    # Browser → Django
    re_path(
        r"ws/camera/"
        r"(?P<camera_id>[^/]+)/"
        r"view/$",

        CameraViewerConsumer.as_asgi(),
    ),

]