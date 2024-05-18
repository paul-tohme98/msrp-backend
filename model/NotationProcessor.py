import cv2
import numpy as np
from model.Chord import Chord

from model.Note import Note

class NotationProcessor:

    @classmethod
    def extractCircles(self, img):
        img = cv2.bitwise_not(img)
        th2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 255, -2)

        horizontal = th2
        vertical = th2
        rows, cols = vertical.shape

        # Inverse the image, so that lines are black for masking
        verticalInv = cv2.bitwise_not(vertical)
        # Perform bitwise_and to mask the lines with provided mask
        maskedImg = cv2.bitwise_and(img, img, mask=verticalInv)
        # Reverse the image back to normal
        maskedImgInv = cv2.bitwise_not(maskedImg)

        verticalSize = int(cols / 30)
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalSize))  # Change here for vertical lines
        vertical = cv2.erode(vertical, verticalStructure, (-1, -1))
        vertical = cv2.dilate(vertical, verticalStructure, (-1, -1))

        horizontalSize = int(rows / 20)
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalSize, 1))
        horizontal = cv2.erode(horizontal, horizontalStructure, (-1, -1))
        horizontal = cv2.dilate(horizontal, horizontalStructure, (3, 3))

        horizontal = cv2.bitwise_not(horizontal)
        return horizontal

    @classmethod
    def detectCircles(self, image):
        notesDetected = []

        # Perform adaptive thresholding
        imageThreshold = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, -2)

        # Find contours
        contours, _ = cv2.findContours(imageThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours based on their x-coordinate
        contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[0])

        # Draw green rectangles around the valid contours on a copy of the original image
        imageWithContours = image.copy()

        # Create a mask to determine the color to fill based on intensity
        mask = (image < 128).astype(np.uint8)  # Assume black notes have lower intensity

        # Create a stencil image with the same shape as the input image
        stencil = np.zeros(imageWithContours.shape, dtype=np.uint8)

        # Draw contours on the stencil image with selective filling based on the mask
        for cnt in contours:
            # Calculate the aspect ratio and width of the bounding rectangle
            x, y, w, h = cv2.boundingRect(cnt)
            aspectRatio = float(w) / h

            # Set thresholds for aspect ratio and maximum width to consider only square contours with reasonable width
            aspectRatioThreshold = 0.8
            maxWidthThreshold = 18  # Adjust this threshold as needed

            if 1 - aspectRatioThreshold < aspectRatio < 1 + aspectRatioThreshold and w < maxWidthThreshold:
                # Create a temporary image for drawing the contours
                tempImage = np.zeros_like(image, dtype=np.uint8)
                cv2.drawContours(tempImage, [cnt], -1, (255, 255, 255), thickness=cv2.FILLED)

                # Use the mask to selectively fill only where the mask is non-zero
                stencil[mask != 0] = tempImage[mask != 0]

                # Draw green rectangles around the valid contours on a copy of the original image
                cv2.rectangle(imageWithContours, (x, y), (x + w, y + h), (0, 255, 0), 1)
                # Extract individual contour images and append to the list
                contourImage = np.zeros_like(image, np.uint8)
                contourImage[mask != 0] = tempImage[mask != 0]

                # Calculate the weighted average of the pixel coordinates using pixel values as weights
                roi = image[y:y + h, x:x + w]
                weightedCx = np.average(np.arange(x, x + w), weights=roi.sum(axis=0))
                weightedCy = np.average(np.arange(y, y + h), weights=roi.sum(axis=1))

                cxy = (weightedCx, weightedCy)

                note = Note(None, None, cxy)
                note.image = contourImage

                notesDetected.append(note)

        return imageWithContours, notesDetected

    @classmethod
    def boxNotes(self, line, listNotations, listNotes):
        listChordNotes = []
        listChords = []
        for i, note in enumerate(listNotes):
            for j, notation in enumerate(listNotations):
                if (note.centerCoordinates[0] >= notation["diagonalCoordinates"][0][0] and 
                    note.centerCoordinates[0] <= notation["diagonalCoordinates"][1][0] and
                    note.centerCoordinates[1] <= notation["diagonalCoordinates"][0][1] and
                    note.centerCoordinates[1] >= notation["diagonalCoordinates"][1][1]):

                    if (notation["prediction"] == "noir"):
                        note.duration = 1
                        self.detectPitch(line, note)

                    elif(notation["prediction"] == "chord"):
                        self.processChords(note)
                        self.breakChordNotes(note.diagonalCoordinates, listChordNotes)

                    elif (notation["prediction"] == "blanche"):
                        note.duration = 2
                        self.detectPitch(line, note)

                    elif (notation["prediction"] == "rond"):
                        note.duration = 4
                        self.detectPitch(line, note)

                    elif (notation["prediction"] == "croche"):
                        note.duration = 0.5
                        self.detectPitch(line, note)

                    elif (notation["prediction"] == "double_croche"):
                        note.duration = 0.25
                        self.detectPitch(line, note)
                    
                    # if(notation["prediciton"] == "noir" or notation["prediciton"] == "blanche" or notation["prediciton"] == "croche" or notation["prediciton"] == "double_croche"):
                    #     self.detectPitch(note)
                # line.notes.append(note)
        self.reassembleChordNotes(listChordNotes, listChords)
        for chord in listChords:
            for note in chord.notes:
                self.detectPitch(line, note)
        line.chords = listChords

    @classmethod
    def detectPitch(self, line, note, padding=0):
        height, width = line.imageOriginal.shape[:2]
        if(height >= 80):
            padding = 15

        if (note.centerCoordinates[0] > 25):
            if(note.centerCoordinates[1] < 58 + padding and note.centerCoordinates[1] >= 54 + padding):
                note.pitch = "c3"
            elif(note.centerCoordinates[1] < 54 + padding and note.centerCoordinates[1] >= 50 + padding):
                note.pitch = "d3"
            elif(note.centerCoordinates[1] < 50 + padding and note.centerCoordinates[1] >= 46 + padding):
                note.pitch = "e3"
            elif(note.centerCoordinates[1] < 46 + padding and note.centerCoordinates[1] >= 42 + padding):
                note.pitch = "f3"
            elif(note.centerCoordinates[1] < 42 + padding and note.centerCoordinates[1] >= 38 + padding):
                note.pitch = "g3"
            elif(note.centerCoordinates[1] < 38 + padding and note.centerCoordinates[1] >= 34 + padding):
                note.pitch = "a3"
            elif(note.centerCoordinates[1] < 34 + padding and note.centerCoordinates[1] >= 30 + padding):
                note.pitch = "b3"
            elif(note.centerCoordinates[1] < 30 + padding and note.centerCoordinates[1] >= 26 + padding):
                note.pitch = "c4"
            elif(note.centerCoordinates[1] < 26 + padding and note.centerCoordinates[1] >= 22 + padding):
                note.pitch = "d4"
            elif(note.centerCoordinates[1] < 22 + padding and note.centerCoordinates[1] >= 18 + padding):
                note.pitch = "e4"
            elif(note.centerCoordinates[1] < 18 + padding and note.centerCoordinates[1] >= 14 + padding):
                note.pitch = "f4"
            elif(note.centerCoordinates[1] < 14 + padding):
                note.pitch = "g4"


    @classmethod
    def processChords(self, chord):
        image = chord.image
        # Threshold the image to create a binary mask of black regions
        _, binaryMask = cv2.threshold(image, 30, 255, cv2.THRESH_BINARY)

        # Find contours in the binary mask
        contours, _ = cv2.findContours(binaryMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Select the largest contour
        largestContour = contours[0]

        # Get the bounding rectangle of the largest contour
        boundingRectangle = cv2.boundingRect(largestContour)

        # Crop the image using the bounding rectangle
        x, y, w, h = boundingRectangle
        croppedImage = image[y:y + h, x:x + w]

        # Extract individual contour images and append to the list
        contourImage = np.zeros_like(croppedImage, np.uint8)

        # Get the coordinates of the bottom-left and top-right corners of the bounding rectangle
        bottomLeft = (x, y + h)
        topRight = (x + w, y)
        chord.diagonalCoordinates = (bottomLeft, topRight)

        # Filter contours based on area to remove small noise
        minContourArea = 2  # Adjust as needed
        blackBlobs = [cnt for cnt in contours if cv2.contourArea(cnt) > minContourArea]

        # Count the found black blobs
        numBlobs = len(blackBlobs)

        # Draw contours on the original image
        outputImage = croppedImage.copy()
        cv2.drawContours(outputImage, blackBlobs, -1, (0, 255, 0), 2)

        # Display the result
        # cv2.imshow("Black Blobs Detection", outputImage)
        # cv2.waitKey(0)
        

    @classmethod
    def breakChordNotes(self, blob, outputList):

        x1, y1 = blob[0]
        x2, y2 = blob[1]
        height = y1 - y2

        xNote = x1 + ((x2 - x1) / 2)

        if height <= 10:
            yNote = y2 + height / 2

            cxy = (xNote, yNote)
            note = Note(None, 1, cxy)

            outputList.append(note)

        elif height <= 20:
            yNoteUpper = y2 + height / 4
            yNoteLower = y2 + 3 * (height / 4)
            
            noteUpper = Note(None, 1, (xNote, yNoteUpper))
            noteLower = Note(None, 1, (xNote, yNoteLower))

            outputList.append(noteUpper)
            outputList.append(noteLower)

        elif height <= 30:
            avg = height / 3

            yNoteUpper = y2 + (2 * avg) + (avg / 2)
            yNoteCenter = y2 + 3 * (avg / 2) # height / 2 pou trouver le centre (note centrale)
            yNoteLower = y2 + avg / 2

            noteUpper = Note(None, 1, (xNote, yNoteUpper))
            noteCenter = Note(None, 1, (xNote, yNoteCenter))
            noteLower = Note(None, 1, (xNote, yNoteLower))

            outputList.append(noteUpper)
            outputList.append(noteCenter)
            outputList.append(noteLower)

    @classmethod
    def reassembleChordNotes(self, listChordNotes, listChords):
        notes_by_x = {}
        for note in listChordNotes:
            note.duration = 1
            # print("Center coordinates : ", note.centerCoordinates)
            x = note.centerCoordinates[0]
            if x not in notes_by_x:
                notes_by_x[x] = []
            notes_by_x[x].append(note)
        
        # Iterate through grouped notes and create chords
        for x, notes in notes_by_x.items():
            chord = Chord(notes)  # Create a Chord object with the list of notes
            listChords.append(chord)  # Append the Chord object to the list of chords

