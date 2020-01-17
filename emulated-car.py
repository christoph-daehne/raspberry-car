import cv2
import socketio
import sys
import threading
import time

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
        self._camera = cv2.VideoCapture(0)
        self._stopAtTime = AtomicInteger(0)

    @property
    def stopAtTime(self):
        return self._stopAtTime.value

    @stopAtTime.setter
    def stopAtTime(self, seconds):
        self._stopAtTime.value = seconds

    def stream(self):
        while True:
            if self.stopAtTime > round(time.time()):
                self._sendFrame()
            else:
                time.sleep(1)

    def _sendFrame(self):
        # Grab a single frame of video
        ret, frame = self._camera.read()
        # Resize frame of video to 1/4 size for performance
        frameSmall = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # encode data as JPEG (for now)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        frameJpeg = cv2.imencode('.jpg', frameSmall, encode_param)
        frameBytes = frameJpeg[1].tobytes()
        # send data as message
        self._sio.emit('video', frameBytes)
        print('sent camera frame, number of bytes: ', len(frameBytes))

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
