import cv2
import socketio
import sys
import threading
import time

class AtomicInteger:
    """
        thread-safe integer
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

class Camera:
    """
        camera to be enabled/disabled and auto-calibrated
    """
    def __init__(self):
        self._camera = None

    def _enableUnlessEnabled(self):
        if self._camera == None:
            self._camera = cv2.VideoCapture(0)

    def disable(self):
        self._camera = None

    def capture(self):
        # power up camera
        self._enableUnlessEnabled()
        # Grab a single frame of video
        ret, frame = self._camera.read()
        # Resize frame of video to 1/4 size
        frameSmall = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # encode data as JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        frameJpeg = cv2.imencode('.jpg', frameSmall, encode_param)
        # get bytes
        frameBytes = frameJpeg[1].tobytes()
        return frameBytes

class VideoStreamer:
    """
        Meant to be run by background worker
        to send camera captures to clients.
    """
    def __init__(self, sio):
        self._sio = sio
        self._camera = Camera()
        self._stopAtTime = AtomicInteger(0)

    @property
    def stopAtTime(self):
        """
            point in time after which no frames are sent
        """
        return self._stopAtTime.value

    @stopAtTime.setter
    def stopAtTime(self, seconds):
        self._stopAtTime.value = seconds

    def stream(self):
        # limit frame rate to upper bound
        maxFps = 5
        minSendingTime = 1/maxFps
        while True:
            now = time.time()
            if self.stopAtTime > round(now):
                self._sio.emit('video', self._camera.capture())
                sendingTime = time.time() - now
                delay = minSendingTime - sendingTime
                if delay > 0:
                    # wait before sending next frame
                    # to stay at maximal frame rate
                    time.sleep(delay)
            else:
                self._camera.disable()
                # busy-waiting: works for now, is not efficient
                time.sleep(1)

sio = socketio.Client()
videoStreamer = VideoStreamer(sio)

@sio.event
def connect():
    print('connected to server')

@sio.event
def command(cmd):
    isStopped = cmd == 'stop'
    # stop video stream after 10 s (unless car is moving)
    videoStreamer.stopAtTime = round(time.time()) + (10 if isStopped else 99999999) 
    print('command: ', cmd)

@sio.event
def disconnect():
    print('disconnected from server')


if __name__ == '__main__':
    try:
        sio.connect(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3000')
        videoStreamWorker = threading.Thread(target=videoStreamer.stream, args=(), daemon=True)
        videoStreamWorker.start()
        sio.wait()
    except KeyboardInterrupt:
        print('bye')