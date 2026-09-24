import asyncio
import time

from channels.generic.websocket import AsyncWebsocketConsumer

from .frame_manager import (
    frame_manager,
    esp32_manager,
)


class CameraUploadConsumer(
    AsyncWebsocketConsumer
):

    async def connect(self):

        self.camera_id = (
            self.scope["url_route"]
            ["kwargs"]["camera_id"]
        )

        await self.accept()

        esp32_manager.register(
            self.camera_id,
            self,
        )

        print(
            f"[CAMERA CONNECTED] "
            f"{self.camera_id}"
        )

    async def disconnect(
        self,
        close_code,
    ):

        esp32_manager.unregister(
            self.camera_id,
            self,
        )

        print(
            f"[CAMERA DISCONNECTED] "
            f"{self.camera_id} "
            f"code={close_code}"
        )

    async def receive(
        self,
        text_data=None,
        bytes_data=None,
    ):

        # -----------------------------
        # FRAME FROM ESP32
        # -----------------------------

        if bytes_data is not None:

            await frame_manager.publish(
                bytes_data
            )

            return

        # -----------------------------
        # TEXT MESSAGE FROM ESP32
        # -----------------------------

        if text_data is not None:

            print(
                f"[ESP32 MESSAGE] "
                f"{text_data}"
            )


class CameraViewerConsumer(
    AsyncWebsocketConsumer
):

    async def connect(self):

        self.camera_id = (
            self.scope["url_route"]
            ["kwargs"]["camera_id"]
        )

        await self.accept()

        print(
            f"[VIEWER CONNECTED] "
            f"{self.camera_id}"
        )

        self.running = True

        self.sender_task = (
            asyncio.create_task(
                self.stream_frames()
            )
        )

    async def disconnect(
        self,
        close_code,
    ):

        self.running = False

        if hasattr(
            self,
            "sender_task"
        ):

            self.sender_task.cancel()

        print(
            f"[VIEWER DISCONNECTED] "
            f"{self.camera_id} "
            f"code={close_code}"
        )

    async def receive(
        self,
        text_data=None,
        bytes_data=None,
    ):

        # Browser can send commands
        # through the viewer WebSocket.

        if text_data is None:
            return

        if text_data == "flash_on":

            success = (
                await esp32_manager
                .send_command(
                    self.camera_id,
                    "FLASH_ON",
                )
            )

            await self.send(
                text_data=(
                    "flash_on_ok"
                    if success
                    else "esp32_offline"
                )
            )

        elif text_data == "flash_off":

            success = (
                await esp32_manager
                .send_command(
                    self.camera_id,
                    "FLASH_OFF",
                )
            )

            await self.send(
                text_data=(
                    "flash_off_ok"
                    if success
                    else "esp32_offline"
                )
            )

    async def stream_frames(self):

        last_frame_number = 0

        last_sent_time = 0.0

        while self.running:

            (
                frame,
                frame_number,
            ) = await (
                frame_manager
                .wait_for_new_frame(
                    last_frame_number,
                    timeout=2.0,
                )
            )

            if frame is None:
                continue

            now = time.monotonic()

            # Maximum ~20 FPS
            if (
                now - last_sent_time
                < 0.05
            ):

                continue

            last_sent_time = now

            last_frame_number = (
                frame_number
            )

            try:

                await self.send(
                    bytes_data=frame
                )

            except Exception as exc:

                print(
                    f"[VIEWER ERROR] "
                    f"{exc}"
                )

                self.running = False

                break