import asyncio
import cv2
import time

# also see https://github.com/balena-labs-projects/balena-cam/blob/master/balena-cam/app/server.py
class Camera():
    def __init__(self):
        self._capture = None
        self._width = 320
        self._height = 256
        # camera is attached to car upside down
        self._rotationMatrix = cv2.getRotationMatrix2D(
            (self._width/2, self._height/2),
            180,
            1.0)

    async def capture(self):
        if self._enableUnlessEnabled():
            encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 50)
            frame = await self._get_latest_frame()
            frameJpeg = cv2.imencode('.jpg', frame, encode_param)
            return frameJpeg[1].tobytes()
        return bytearray()
    
    def _enableUnlessEnabled(self):
        if self._capture == None:
            self._capture = cv2.VideoCapture(0)
            self._capture.set(3, self._width)
            self._capture.set(4, self._height)
            ret, frame = self._capture.read()
            if not ret:
                print('Failed to open default camera.')
                self._capture = None
                return False
        return True

    async def _get_latest_frame(self):
        ret, frame = self._capture.read()
        await asyncio.sleep(0)
        return self._rotate(frame)

    def _rotate(self, frame):
        frame = cv2.warpAffine(
            frame,
            self._rotationMatrix,
            (self._width, self._height))
        return frame
    
    def disable(self):
        if self._capture != None:
            self._capture.release()
            self._capture = None
