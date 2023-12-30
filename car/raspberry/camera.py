import cv2
# https://picamera.readthedocs.io/en/release-1.13/
from picamera import PiCamera
from picamera.array import PiRGBArray
import time

class Camera:
    """
        camera to capture images
    """
    def __init__(self):
        self._camera = None
        self._width = 320
        self._height = 256
        # camera is attached to car upside down
        self._rotationMatrix = cv2.getRotationMatrix2D((self._width/2, self._height/2), 180, 1.0)

    # !!! TODO: must become async !!!
    def capture(self):
        self._enableUnlessEnabled()
        # capture frame
        capture = PiRGBArray(self._camera, size=(self._width, self._height))
        self._camera.capture(capture, format="bgr") # !!! TODO: must become async !!!
        frame = capture.array
        # rotate (since camera is attached upside down)
        frameRotated = cv2.warpAffine(frame, self._rotationMatrix, (self._width, self._height))
        # compress
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        frameJpeg = cv2.imencode('.jpg', frameRotated, encode_param)
        # send to controller
        frameBytes = frameJpeg[1].tobytes()
        return frameBytes

    def _enableUnlessEnabled(self):
        if self._camera == None:
            self._camera = PiCamera()
            self._camera.resolution = (self._width, self._height)
            self._camera.framerate = 60
            # https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images
            # high ISO for lower shutter speed thus better images while moving
            self._camera.iso = 1200
            # Wait for the automatic gain control to settle
            time.sleep(2) # !!! TODO: must become async !!!
            # Now fix the values
            self._camera.shutter_speed = self._camera.exposure_speed
            self._camera.exposure_mode = 'off'
            awb_gains = self._camera.awb_gains
            self._camera.awb_mode = 'off'
            self._camera.awb_gains = awb_gains

    def disable(self):
        if self._camera != None:
            self._camera.close()
            self._camera = None


