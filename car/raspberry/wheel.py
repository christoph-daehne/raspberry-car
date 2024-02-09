import RPi.GPIO as GPIO

def create_wheels():
    GPIO.setmode(GPIO.BOARD)
    # disables the following warning:
    # > This channel is already in use, continuing anyway.
    GPIO.setwarnings(False)
    Left = Wheel(8, 10, 12)
    Right = Wheel(3, 5, 7)
    return [Left, Right]

def close_wheels():
    [LeftWheels, RightWheels] = create_wheels()
    LeftWheels.setSpeed(0)
    RightWheels.setSpeed(0)
    GPIO.cleanup()

class Wheel:
    """
        wheel(s) on one side of the car
    """

    def __init__(self, enPin: int, inForwardPin: int, inBackwardPin: int):
        GPIO.setup(inForwardPin, GPIO.OUT)
        self.inForwardPin = inForwardPin
        GPIO.output(inForwardPin, False)

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
        isForwards = speed > 0
        if (isForwards):
            GPIO.output(self.inBackwardPin, False)
            GPIO.output(self.inForwardPin, True)
        else:
            GPIO.output(self.inForwardPin, False)
            GPIO.output(self.inBackwardPin, force > 0)
        if force > 0:
            self.pwm.ChangeDutyCycle(70 + (10 * force))
        else:
            self.pwm.ChangeDutyCycle(0)
