import time
import os
import nats
import asyncio

CONTEXT = os.environ.get('CONTEXT', 'PRODUCTION');
if CONTEXT == 'EMULATOR':
    from emulator.camera import Camera
    from emulator.wheel import create_wheels, close_wheels
else:
    from raspberry.camera import Camera
    from raspberry.wheel import create_wheels, close_wheels

print("""
Starting service app to run on the raspberry PI.
Receives commands for direction and sends video frames.
""")

class VideoStreamer:
    """
        Meant to be run as a coroutine in an event loop
        to send camera captures to clients.
    """
    def __init__(self):
        self._camera = Camera()
        self.stopAtTime = 0

    async def stream(self, sendFrame):
        maxFps = 5
        minSendingTime = 1/maxFps
        while True:
            now = time.time()
            if self.stopAtTime > round(time.time()):
                await sendFrame(await self._camera.capture())
                sendingTime = time.time() - now
                delay = minSendingTime - sendingTime
                if delay > 0:
                    await asyncio.sleep(delay)
            else:
                self._camera.disable()
                await asyncio.sleep(1)

async def mainVideoStream(nc, topic: str, videoStreamer: VideoStreamer):
    async def sendFrame(bytes):
        await nc.publish(topic, bytes)
    await videoStreamer.stream(sendFrame)

async def mainProcessCommands(nc, topic: str, videoStreamer: VideoStreamer):
    [LeftWheels, RightWheels] = create_wheels()
    async def setSpeed(speedLeft: int, speedRight: int):
        # stop video stream after 10 s (unless car is moving)
        isStopped = speedLeft == 0 and speedRight == 0
        videoStreamer.stopAtTime = round(time.time()) + (10 if isStopped else 99999999)
        # adjust speed
        LeftWheels.setSpeed(speedLeft)
        RightWheels.setSpeed(speedRight)
    async def drive(message):
        command = message.data.decode()
        speedLeft = 0
        speedRight = 0
        if command == "Foreward":
            speedLeft = 3
            speedRight = 3
        elif command == "Back":
            speedLeft = -2
            speedRight = -2
        elif command == "Left":
            speedLeft = -1
            speedRight = 1
        elif command == "Right":
            speedLeft = 1
            speedRight = -1
        await setSpeed(speedLeft, speedRight)
    commands = await nc.subscribe(topic)
    lastCommand = round(time.time())
    while True:
        async for message in commands.messages:
            await drive(message)
            lastCommand = round(time.time())
        # stop after a few seconds without command
        if lastCommand + 2 < round(time.time()):
            await setSpeed(0, 0)
            lastCommand = round(time.time())
        await asyncio.sleep(1)

async def main():
    natsUrl = os.environ.get("NATS_URL", "nats://localhost:4222")
    natsTopic = os.environ.get("NATS_TOPIC", "")
    assert natsTopic != "", "expecting unset NATS_TOPIC, eg 'de.sandstorm.raspberry.car.1'"
    natsCreds = os.environ.get("NATS_CREDS")
    nc = await nats.connect(natsUrl, user_credentials=natsCreds)
    videoStreamer = VideoStreamer()
    await asyncio.gather(
        mainVideoStream(nc, natsTopic + ".images", videoStreamer),
        mainProcessCommands(nc, natsTopic + ".commands", videoStreamer)
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        close_wheels()
