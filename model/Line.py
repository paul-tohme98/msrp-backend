class Line:
    def __init__(self):
        self.imageOriginal = None
        self.imageStaffRemoved = None
        self.imageAfterDetection = None
        self.imageReconstructed = None
        self.imageWithCircles = None
        self.notations = []
        self.predictions = []
        self.notes = [] # Notes present in a line
        self.chords = [] # Chords present of a line
        self.key = None # The key of the line
