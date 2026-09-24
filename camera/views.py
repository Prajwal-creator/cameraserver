import json

from django.http import JsonResponse
from django.shortcuts import render

from .frame_manager import (
    frame_manager,
    esp32_manager,
)


def dashboard(request):

    return render(
        request,
        "camera/index.html"
    )


def camera_status(request):

    stats = frame_manager.statistics()

    age = stats["last_frame_age"]

    online = (
        age is not None
        and age < 3
    )

    esp32_online = (
        esp32_manager
        .is_connected(
            "esp32cam-01"
        )
    )

    return JsonResponse({

        "online": online,

        "esp32_connected":
            esp32_online,

        "status":
            "LIVE"
            if online
            else "OFFLINE",

        "frame_number":
            stats["frame_number"],

        "frame_size":
            stats["frame_size"],

        "last_frame_age":
            age,

    })


async def flash_control(
    request,
    camera_id,
):

    if request.method != "POST":

        return JsonResponse(
            {
                "error":
                    "POST required"
            },
            status=405,
        )

    try:

        data = json.loads(
            request.body
        )

    except Exception:

        return JsonResponse(
            {
                "error":
                    "Invalid JSON"
            },
            status=400,
        )

    state = data.get("state")

    if state == "on":

        command = "FLASH_ON"

    elif state == "off":

        command = "FLASH_OFF"

    else:

        return JsonResponse(
            {
                "error":
                    "state must be on or off"
            },
            status=400,
        )

    success = await esp32_manager.send_command(
        camera_id,
        command,
    )

    if not success:

        return JsonResponse(
            {
                "success": False,
                "error":
                    "ESP32 is offline",
            },
            status=503,
        )

    return JsonResponse({

        "success": True,

        "camera_id":
            camera_id,

        "flash":
            state,

    })