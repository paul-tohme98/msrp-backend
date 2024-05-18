import cv2
import numpy as np
import os
import glob


class NotationSaving:

    @classmethod
    def saveSymbols(self, extractedLines):
        # print("Saving...")
        count = 0
        for line in extractedLines:
            notations = []
            for idx, notation in enumerate(line.notations):
                cv2.imwrite(f"./contours/{count+1}.png", notation["image"])
                notations.append(notation)
                count = count + 1

    @classmethod
    def resizeContours(self, contourPath, indice):
        # print("Resizing...")
        # Load the image
        image = cv2.imread(contourPath)

        # Convert the image to grayscale
        grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Find the contours of the digit
        contours, _ = cv2.findContours(grayscaleImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort the contours by their area in descending order
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Select the largest contour
        largestContour = contours[0]

        # Get the bounding rectangle of the largest contour
        boundingRectangle = cv2.boundingRect(largestContour)

        # Crop the image using the bounding rectangle
        x, y, w, h = boundingRectangle
        croppedImage = image[y:y + h, x:x + w]

        # Save the cropped image
        cv2.imwrite(f'./contours_resized/{indice+1}.png', croppedImage)

    @classmethod
    def organize(self, lines):
        # Use glob to get a list of all PNG files in the folder
        pngFiles = glob.glob(os.path.join("./contours_resized", "*.png"))
        pngFiles.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

        count = 0
        for idx, line in enumerate(lines):
            limit = count + len(line.notations)
            lower = count
            # print(f"count = {count}")
            # print(f"limit = {limit}")
            # print("--------------------------------------------")
            #  Create a subdirectory for each line
            lineSymbolsDir = os.path.join("./contours_resized", f"line_{idx+1}/")
            os.makedirs(lineSymbolsDir, exist_ok=True)

            for i, notation in enumerate(pngFiles):
                img = cv2.imread(notation)
                if i < limit and i >= lower:
                    cv2.imwrite(os.path.join(lineSymbolsDir, f"{i+1}.png"), img)   
                count += 1 
            count = limit
        
        # Replace 'your_directory_path' with the path to your directory
        directoryPath = './contours_resized'

        # Call the function to remove files in the specified directory
        self.removeFiles(directoryPath)


    @classmethod
    def removeFiles(self, directoryPath):
        # List all files in the directory
        files = os.listdir(directoryPath)

        # Iterate over each file in the directory
        for fileName in files:
            # Construct the full path to the file
            filePath = os.path.join(directoryPath, fileName)

            # Check if it's a file (not a subdirectory)
            if os.path.isfile(filePath):
                # Remove the file
                os.remove(filePath)
                #print(f"Removed: {file_path}")
