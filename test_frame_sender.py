import asyncio
import struct

import websockets


WIDTH = 320
HEIGHT = 240

UPLOAD_URL = (
    "ws://127.0.0.1:8000/"
    "ws/camera/esp32cam-01/upload/"
)


def create_rgb565_frame(frame_number):

    frame = bytearray(WIDTH * HEIGHT * 2)

    for y in range(HEIGHT):

        for x in range(WIDTH):

            # Moving test pattern
            r = (x + frame_number * 2) % 256
            g = (y + frame_number * 2) % 256
            b = ((x + y) + frame_number * 2) % 256

            # RGB888 → RGB565
            r5 = r >> 3
            g6 = g >> 2
            b5 = b >> 3

            rgb565 = (
                (r5 << 11)
                | (g6 << 5)
                | b5
            )

            index = (y * WIDTH + x) * 2

            # Little-endian RGB565
            frame[index] = rgb565 & 0xFF
            frame[index + 1] = (
                rgb565 >> 8
            ) & 0xFF

    return bytes(frame)


async def main():

    print("Connecting to Django...")
    print(UPLOAD_URL)

    async with websockets.connect(
        UPLOAD_URL,
        max_size=None,
    ) as websocket:

        print("Connected!")
        print("Sending test frames...")

        frame_number = 0

        while True:

            frame = create_rgb565_frame(
                frame_number
            )

            await websocket.send(frame)

            frame_number += 1

            print(
                f"Frame {frame_number} "
                f"sent: {len(frame)} bytes"
            )

            # 10 FPS
            await asyncio.sleep(0.1)


if __name__ == "__main__":

    asyncio.run(main())