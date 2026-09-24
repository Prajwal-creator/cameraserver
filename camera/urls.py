from django.urls import path

from .views import (
    dashboard,
    camera_status,
    flash_control,
)


urlpatterns = [

    path(
        "",
        dashboard,
        name="dashboard",
    ),

    path(
        "api/camera/status/",
        camera_status,
        name="camera-status",
    ),

    path(
        "api/camera/<str:camera_id>/flash/",
        flash_control,
        name="camera-flash",
    ),

]