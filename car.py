import socketio
import RPi.GPIO as GPIO
import time
import sys
 
print("""
Socket.io client for the car.
Connects to server and receives commands and events.
""")
 
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

    def driveForeward():
        print('driving foreward')
        LeftWheels.setSpeed(3)
        RightWheels.setSpeed(3)

    def driveLeft():
        print('driving left')
        LeftWheels.setSpeed(-3)
        RightWheels.setSpeed(3)

    def driveRight():
        print('driving right')
        LeftWheels.setSpeed(3)
        RightWheels.setSpeed(-3)

    def driveStop():
        print('full stop')
        LeftWheels.setSpeed(0)
        RightWheels.setSpeed(0)

    sio = socketio.Client()
    try:
        @sio.event
        def connect():
            print('connected to server')
            # a LED would be handy
            driveStop()

        @sio.event
        def command(data):
            if data == 'left':
                driveLeft()
            elif data == 'right':
                driveRight()
            elif data == 'foreward':
                driveForeward()
            elif data == 'stop':
                driveStop()
            else:
                print("unknown command '%s'" % data)
                driveStop()

        @sio.event
        def disconnect():
            print('disconnected from server')
            # a LED would be handy
            driveStop()

        sio.connect(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3000')
        sio.wait()
    except KeyboardInterrupt:
        LeftWheels.setSpeed(0)
        RightWheels.setSpeed(0)
        GPIO.cleanup()
        print('bye')
