import glob
import os
import cv2
import numpy as np
import tkinter as tk
from scamp import Session

from model.Line import Line
from model.LineProcessor import LineProcessor
from model.NotationProcessor import NotationProcessor
from model.NotationSaving import NotationSaving
from model.CnnPrediction import CnnPrediction
from model.SoundGenerator import SoundGenerator

class BackendMain:
    @classmethod
    def processSheet(self, imagePath):
        print("******************************************")
        print("          Welcome to the MSRP!")
        print("******************************************")
        

        extractedLines = []

        listOutput = []

        outputFile = "./output.txt"

        outputMp3 = "./sounds/output.mp3"

        binImg = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
        print("Shape input : ", binImg.shape)

        # binImg = cv2.resize(binImg, (933 ,811))

        if binImg is None:
            raise Exception(f"Error: Unable to load the image at '{imagePath}'")

        height, width = binImg.shape[:2]
        resizedImg = cv2.resize(binImg, (int(width * 1), int(height * 1)))

        print("Extracting staff lines...")

        extractedImages = LineProcessor.extractStaffLines(resizedImg)

        # For each line from the sheet
        for lineImage in extractedImages:

            imageWithoutStaffLines = LineProcessor.removeStaffLines(lineImage)
            
            withRecognition, notationsPerLine = LineProcessor.detectSymbols(imageWithoutStaffLines)

            withCircles = NotationProcessor.extractCircles(imageWithoutStaffLines)

            withCircles, circlesDetected = NotationProcessor.detectCircles(withCircles)

            reconstructedImage = LineProcessor.reconstructStaffLines(withCircles.copy())

            line = Line()
            line.imageOriginal = lineImage
            line.imageStaffRemoved = imageWithoutStaffLines
            line.imageAfterDetection = withRecognition
            line.imageReconstructed = reconstructedImage
            line.imageWithCircles = withCircles

            line.notations = notationsPerLine
            line.notes = circlesDetected
        
            extractedLines.append(line)

        print("In total we have : ", len(extractedLines), " lines")

        print("Saving...")
        NotationSaving.saveSymbols(extractedLines)
        print("Symbols are saved sucessfully!")

        folderPath = "./contours/"  # Replace this with the path to your folder

        # Use glob to get a list of all PNG files in the folder
        pngFiles = glob.glob(os.path.join(folderPath, "*.png"))
        pngFiles.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
        # print("We found ", len(png_files), " images")

        count = 0
        print("Resizing...")
        # Loop over each PNG file
        for count, pngFile in enumerate(pngFiles): 
            # print(f"Processing {png_file}")
            NotationSaving.resizeContours(pngFile, count)
            count +=1
        print("Symbols are resized successfully!")

        print("Organize...")
        NotationSaving.organize(extractedLines)
        print("Organizing Done!")

            # List all items in the directory
        items = os.listdir("./contours_resized")

        # Filter out only the subdirectories
        subdirs = [item for item in items if os.path.isdir(os.path.join("./contours_resized", item))]

        for id, dir in enumerate(subdirs):
            symbols = glob.glob(os.path.join("./contours_resized", dir, "*.png"))
            symbols.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            #print(symbols)

            listSymbols = []
            #print("Filling the list...")
            for idx, symbol in enumerate(symbols):
                img = cv2.imread(symbol)

                # Check if the image is grayscale
                if len(img.shape) == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                listSymbols.append(img)
                
            #print("List is full!")
            print(f"Predicting notations line {dir}...")
            extractedLines[id].predictions = CnnPrediction.prediction(listSymbols)

            for idn, cnt in enumerate(extractedLines[id].notations):
                cnt["prediction"] = extractedLines[id].predictions[idn]

        for idx, line in enumerate(extractedLines):
            print("********************************************************")
            print("                     Line ", idx + 1)
            print("********************************************************")
            print("Coordniates found : ", len(line.notations))
            print("Size : ", line.imageOriginal.shape)

            for i, n in enumerate(line.notations):
                if n["prediction"] == "point":
                    if i > 0 and i < len(line.notations) - 1:
                        if line.notations[i - 1]["prediction"] == "point" and line.notations[i + 1]["prediction"] == "point":
                            n["prediction"] = "rond"
                            
                # print("Prediction : ", n["prediction"], "\t", "Diagonal coordinates : ", n["diagonalCoordinates"])


            NotationProcessor.boxNotes(line, line.notations, line.notes)
            
            # Iterate over sorted notes and print each note or chord at its correct position in the line
            for idNote, note in enumerate(line.notes):
                if(len(line.chords) > 0):
                    for chord in line.chords:
                        if (chord.isDisplayed == False) and (chord.notes[0].centerCoordinates[0] > note.centerCoordinates[0] and chord.notes[0].centerCoordinates[0] < line.notes[idNote + 1].centerCoordinates[0]):
                            listOutput.append([(note.pitch, note.duration) for note in chord.notes])
                            print("Chord pitches and durations: ", [(note.pitch, note.duration) for note in chord.notes])
                            chord.isDisplayed = True
                    
                    if (note.pitch != None):  
                        listOutput.append((note.pitch, note.duration))  
                        print("Pitch:", note.pitch, "\tDuration:", note.duration)
                elif (note.pitch != None):
                    listOutput.append((note.pitch, note.duration)) 
                    print("Pitch:", note.pitch, "\tDuration:", note.duration)                    

        SoundGenerator.saveToTextFile(outputFile, listOutput)

        for idx, line in enumerate(extractedLines):
        #     # cv2.imwrite(f'./lines/{idx + 1}.png', line.imageStaffRemoved)
            cv2.imshow(f"Original Line {idx + 1}", line.imageOriginal)
            cv2.imshow(f"Line {idx + 1}", line.imageWithCircles)
            cv2.imshow(f"Staff lines removed : Line {idx + 1}", line.imageStaffRemoved)
            cv2.imshow(f"After detection : Line {idx + 1}", line.imageAfterDetection)
            cv2.imshow(f"Reconstructed Staff Lines {idx}", line.imageReconstructed)
            cv2.imshow(f"Processed Image with Contours : Line {idx + 1}", line.imageWithCircles)
            cv2.waitKey(0)

        # cv2.destroyAllWindows()
        print(listOutput)

        # instrumentChoice = "piano"
        # session = Session()
        # # SoundGenerator.playMidiNotes(session, listOutput, instrumentChoice)
        # SoundGenerator.saveAsMp3(session, listOutput, instrumentChoice)

        return listOutput

    @classmethod
    def playMidi(self, listOutput):
        file = None
        instrumentChoice = "piano"
        session = Session()
        SoundGenerator.playMidiNotes(session, listOutput, instrumentChoice)
        file = SoundGenerator.saveAsMp3(session, listOutput, instrumentChoice)

        return file

if __name__ == "__main__":
    imagePath = "./input/usecase.png"
    # Read the image
    img = cv2.imread(imagePath)

    # Get the original dimensions of the image
    height, width = img.shape[:2]

    # Resize the image to 80% of its original size
    new_width = int(width * 0.8)
    new_height = int(height * 0.8)
    resized_img = cv2.resize(img, (new_width, new_height))

    # Display the resized image (optional)
    cv2.imshow('Input Image', resized_img)
    cv2.waitKey(0)
    listOutput = BackendMain.processSheet(imagePath)
    print("*************************************** List of notes ***************************************")
    print(listOutput)
    file = BackendMain.playMidi(listOutput)
    print(file)
    