import time

class Camera:
    """
        dummy camera to send frames from fixture files
    """
    def __init__(self):
        with open("../test-image-1.jpg", mode="rb") as file:
            self._frame1 = file.read()
        with open("../test-image-2.jpg", mode="rb") as file:
            self._frame2 = file.read()

    async def capture(self):
        nowSeconds = round(time.time())
        # we want to change the frame every second
        if nowSeconds % 2 == 0:
            return self._frame1
        else:
            return self._frame2

    def disable(self):
        pass
