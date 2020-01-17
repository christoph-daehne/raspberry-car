import cv2
import socketio
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import sys
import threading
import io
 
print("""
Socket.io client for the car.
Connects to server and receives commands and events.
""")

class AtomicInteger():
    """
        thread-safe interger
        thanks to https://stackoverflow.com/questions/23547604/python-counter-atomic-increment
    """
    def __init__(self, value=0):
        self._value = value
        self._lock = threading.Lock()

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, v):
        with self._lock:
            self._value = v
            return self._value

class VideoStreamer:
    """
        Meant to be run by background worker
        to send camera captures to clients.
    """
    def __init__(self, sio):
        self._sio = sio
        self._camera = PiCamera()
        self._width = 160
        self._height = 128
        self._camera.resolution = (self._width, self._height)
        self._camera.framerate = 60
        self._stopAtTime = AtomicInteger(0)
        self._rotationMatrix = cv2.getRotationMatrix2D((self._width/2, self._height/2), 180, 1.0)
        self._numberOfFrames = -1
        self._streamStartTime = -1

    @property
    def stopAtTime(self):
        return self._stopAtTime.value

    @stopAtTime.setter
    def stopAtTime(self, seconds):
        self._stopAtTime.value = seconds

    def stream(self):
        # https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images
        # Set ISO to the desired value
        self._camera.iso = 1200
        # Wait for the automatic gain control to settle
        time.sleep(2)
        # Now fix the values
        self._camera.shutter_speed = self._camera.exposure_speed
        self._camera.exposure_mode = 'off'
        g = self._camera.awb_gains
        self._camera.awb_mode = 'off'
        self._camera.awb_gains = g
        while True:
            if self._isStreaming():
                if self._streamStartTime < 0:
                    self._streamStartTime = time.time()
                    self._numberOfFrames = 0
                self._sendFrame()
                self._numberOfFrames += 1
            else:
                if self._streamStartTime > 0:
                    seconds = time.time() - self._streamStartTime
                    fps = self._numberOfFrames / seconds
                    self._streamStartTime = -1
                    print('fps', fps)
                time.sleep(1)

    def _sendFrame(self):
        # capture frame
        capture = PiRGBArray(self._camera, size=(self._width, self._height))
        self._camera.capture(capture, format="bgr")
        frame = capture.array
        # rotate (since camera is attached upside down)
        frameRotated = cv2.warpAffine(frame, self._rotationMatrix, (self._width, self._height))
        # compress
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        frameJpeg = cv2.imencode('.jpg', frameRotated, encode_param)
        # send to controller
        frameBytes = frameJpeg[1].tobytes()
        self._sio.emit('video', frameBytes)

    def _isStreaming(self):
        return self.stopAtTime > round(time.time())

class Wheel:
    """
        wheel(s) on one side of the car
    """
 
    def __init__(self, enPin: int, inForewardPin: int, inBackwardPin: int):
        GPIO.setup(inForewardPin, GPIO.OUT)
        self.inForewardPin = inForewardPin
        GPIO.output(inForewardPin, False)
 
        self.inBackwardPin = inBackwardPin
        GPIO.setup(inBackwardPin, GPIO.OUT)
        GPIO.output(inBackwardPin, False)
 
        GPIO.setup(enPin, GPIO.OUT)
        self.pwm = GPIO.PWM(enPin, 100)
        self.pwm.start(0)
        self.pwm.ChangeDutyCycle(0)
 
    def setSpeed(self, speed: int):
        """
            speed might be -3, -2, -1, 0, 1, 2, 3
        """
        force = min(3, abs(speed))
        isForewards = speed > 0
        if (isForewards):
            GPIO.output(self.inBackwardPin, False)
            GPIO.output(self.inForewardPin, True)
        else:
            GPIO.output(self.inForewardPin, False)
            GPIO.output(self.inBackwardPin, force > 0)
        if force > 0:
            self.pwm.ChangeDutyCycle(70 + (10 * force))
        else:
            self.pwm.ChangeDutyCycle(0)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    RightWheels = Wheel(3, 5, 7)
    LeftWheels = Wheel(8, 10, 12)

    def drive(speedLeft, speedRight):
        print('driving', speedLeft, speedRight)
        LeftWheels.setSpeed(speedLeft)
        RightWheels.setSpeed(speedRight)

    sio = socketio.Client()
    videoStreamer = VideoStreamer(sio)
    try:
        @sio.event
        def connect():
            print('connected to server')
            # a LED would be handy
            drive(0, 0)

        @sio.event
        def command(data):
            isStopped = data == 'stop'
            # stop video stream after 10 s (unless car is moving)
            videoStreamer.stopAtTime = round(time.time()) + (10 if isStopped else 99999999) 
            if data == 'left':
                drive(-1, 1)
            elif data == 'right':
                drive(1, -1)
            elif data == 'foreward':
                drive(3, 3)
            elif data == 'backward':
                drive(-3, -3)
            elif data == 'stop':
                drive(0, 0)
            else:
                print("unknown command '%s'" % data)
                drive(0, 0)

        @sio.event
        def disconnect():
            print('disconnected from server')
            # a LED would be handy
            drive(0, 0)

        sio.connect(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3000')
        videoStreamWorker = threading.Thread(target=videoStreamer.stream, args=(), daemon=True)
        videoStreamWorker.start()
        sio.wait()
    except KeyboardInterrupt:
        LeftWheels.setSpeed(0)
        RightWheels.setSpeed(0)
        GPIO.cleanup()
        print('bye')
