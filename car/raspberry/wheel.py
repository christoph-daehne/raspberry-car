import RPi.GPIO as GPIO

def create_wheels():
    GPIO.setmode(GPIO.BOARD)
    Left = Wheel(8, 10, 12)
    Right = Wheel(3, 5, 7)
    return [
        Left,
        Right
    ]

def close_wheels():
    GPIO.cleanup()

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
