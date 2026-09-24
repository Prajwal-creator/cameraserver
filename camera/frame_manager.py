import asyncio
import time


class FrameManager:

    def __init__(self):
        self._frame = None
        self._timestamp = 0.0
        self._frame_number = 0

        self._condition = asyncio.Condition()

    async def publish(self, frame: bytes):

        async with self._condition:

            # Keep ONLY newest frame
            self._frame = frame

            self._timestamp = time.monotonic()

            self._frame_number += 1

            self._condition.notify_all()

    async def get_latest(self):

        async with self._condition:
            return self._frame

    async def wait_for_new_frame(
        self,
        last_frame_number,
        timeout=2.0,
    ):

        async with self._condition:

            if self._frame_number > last_frame_number:

                return (
                    self._frame,
                    self._frame_number,
                )

            try:

                await asyncio.wait_for(

                    self._condition.wait_for(

                        lambda:
                        self._frame_number
                        > last_frame_number

                    ),

                    timeout=timeout,
                )

            except asyncio.TimeoutError:

                return (
                    None,
                    last_frame_number,
                )

            return (
                self._frame,
                self._frame_number,
            )

    def statistics(self):

        if self._timestamp == 0:

            age = None

        else:

            age = (
                time.monotonic()
                - self._timestamp
            )

        return {

            "frame_number":
                self._frame_number,

            "frame_size":
                len(self._frame)
                if self._frame
                else 0,

            "last_frame_age":
                age,
        }


class ESP32Manager:

    def __init__(self):

        self.connections = {}

    def register(
        self,
        camera_id,
        consumer,
    ):

        self.connections[camera_id] = consumer

        print(
            f"[ESP32 MANAGER] "
            f"Registered {camera_id}"
        )

    def unregister(
        self,
        camera_id,
        consumer,
    ):

        if self.connections.get(camera_id) is consumer:

            del self.connections[camera_id]

            print(
                f"[ESP32 MANAGER] "
                f"Unregistered {camera_id}"
            )

    async def send_command(
        self,
        camera_id,
        command,
    ):

        consumer = self.connections.get(camera_id)

        if consumer is None:

            return False

        try:

            await consumer.send(
                text_data=command
            )

            return True

        except Exception as exc:

            print(
                f"[ESP32 COMMAND ERROR] {exc}"
            )

            return False

    def is_connected(
        self,
        camera_id,
    ):

        return camera_id in self.connections


frame_manager = FrameManager()

esp32_manager = ESP32Manager()