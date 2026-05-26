import cv2
import numpy as np


class LineProcessor:

    # Extract the lines from the music score given as a bin image
    @classmethod
    def extractStaffLines(self, binImg):
        lines = []
        linesExtracted = []

        # Invert the binary image
        invertedImg = cv2.bitwise_not(binImg)

        # Apply GaussianBlur to the image
        blurredImage = cv2.GaussianBlur(invertedImg, (7, 7), 0)

        # Find contours in the binary image
        contours, _ = cv2.findContours(blurredImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on area and aspect ratio
        minContourArea = 20000
        aspectRatioThreshold = 10000
        staffLineContours = [cnt for cnt in contours if cv2.contourArea(cnt) > minContourArea
                            and aspectRatioThreshold > cnt.shape[0] / cnt.shape[1] > 1 / aspectRatioThreshold]

        # Draw green rectangles around the valid contours
        contourImage = cv2.cvtColor(binImg, cv2.COLOR_GRAY2BGR)
        for cnt in staffLineContours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(contourImage, (x, y), (x + w, y + h), (0, 255, 0), 2)

        #staff_line_contours  = staff_line_contours
        print("Number of staff lines found:", len(staffLineContours))

        for i, contour in enumerate(staffLineContours):
            # Get the bounding box of the contour
            x, y, w, h = cv2.boundingRect(contour)

            # Crop the original image according to the bounding box
            croppedRegion = binImg[y:y + h, x:x + w]

            linesExtracted.insert(0, croppedRegion)
            
        return linesExtracted


    # Detect musical notations (symbols) on the already processed image
    @classmethod
    def detectSymbols(self, image):

        notations = []
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
            notation = {
                "image" : None,
                "diagonalCoordinates" : None,
                "prediction" : ""
            }
            # Create a temporary image for drawing the contours
            tempImage = np.zeros_like(image, dtype=np.uint8)
            cv2.drawContours(tempImage, [cnt], -1, (255, 255, 255), thickness=cv2.FILLED)

            # Use the mask to selectively fill only where the mask is non-zero
            stencil[mask != 0] = tempImage[mask != 0]

            # Draw green rectangles around the valid contours on a copy of the original image
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(imageWithContours, (x, y), (x + w, y + h), (0, 255, 0), 1)

            # Extract individual contour images and append to the list
            contourImage = np.zeros_like(image, np.uint8)
            contourImage[mask != 0] = tempImage[mask != 0]

            notation["image"] = contourImage

            # Get the coordinates of the bottom-left and top-right corners of the bounding rectangle
            bottomLeft = (x, y + h)
            topRight = (x + w, y)
            notation["diagonalCoordinates"] = (bottomLeft, topRight)
            # coordinates.append(cxy)

            notations.append(notation)

        return imageWithContours, notations
    
    # Reconstruct the 5 staff lines
    @classmethod
    def reconstructStaffLines(self, image, numLines=5, lineSpacingFactor=2, verticalOffset=50):
        height, width = image.shape[:2]
        lineSpacing = height // (numLines - 1) // lineSpacingFactor
        verticalOffset = height // 4

        # Draw horizontal lines at expected positions of staff lines
        for i in range(numLines):
            y = verticalOffset + i * lineSpacing
            cv2.line(image, (0, y), (width, y), (0, 0, 0), 1)  # Black lines

        return image

    # Remove the five staff lines of each musical line extracted
    @classmethod
    def removeStaffLines(self, img):
        
        #img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img = cv2.bitwise_not(img)
        #img = cv2.GaussianBlur(img, (17,17), 1)
        th2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 255, -2) # 15

        horizontal = th2
        vertical = th2
        rows,cols = horizontal.shape

        #inverse the image, so that lines are black for masking
        horizontalInv = cv2.bitwise_not(horizontal)
        #perform bitwise_and to mask the lines with provided mask
        maskedImg = cv2.bitwise_and(img, img, mask=horizontalInv)
        #reverse the image back to normal
        maskedImgInv = cv2.bitwise_not(maskedImg)

        horizontalSize = int(cols / 30)
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalSize,1))
        horizontal = cv2.erode(horizontal, horizontalStructure, (-1, -1))
        horizontal = cv2.dilate(horizontal, horizontalStructure, (-1, -1))

        verticalSize = int(rows / 20)
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalSize))
        vertical = cv2.erode(vertical, verticalStructure, (-1, -1))
        vertical = cv2.dilate(vertical, verticalStructure, (3, 3))

        vertical = cv2.bitwise_not(vertical)

        return vertical
