class Note:
    def __init__(self, pitch, duration, centerCoordinates):
        self.image = None
        self.pitch = pitch
        self.duration = duration
        self.centerCoordinates = centerCoordinates
        self.diagonalCoordinates = None
