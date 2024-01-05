
def create_wheels():
    Left = Wheel("left wheel")
    Right = Wheel("right wheel")
    return [
        Left,
        Right
    ]

def close_wheels():
    print("Stopping car and closing GPIO")

class Wheel:
    """
        dummy wheel(s) just logging stiff
    """

    def __init__(self, name: str):
        self._name = name

    def setSpeed(self, speed: int):
        """
            speed might be -3, -2, -1, 0, 1, 2, 3
        """
        print("setting speed of %s to %d" % (self._name, speed))
