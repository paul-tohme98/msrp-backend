from keras.models import load_model
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
import cv2
import numpy as np
import glob
import tensorflow as tf
import os


class CnnPrediction:

    @classmethod
    def prediction(self, notationsOfSingleLine):
        # Load the trained CNN model
        modelPath = 'trained_models/cnn_trained_model_modified.h5'
        cnn = load_model(modelPath)

        trainDatagen = ImageDataGenerator(
            rescale=1. / 255,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
        )

        # Pre-processing test set
        trainingSet = trainDatagen.flow_from_directory(
            'train_data/MuscimaRefined',
            target_size=(64, 64),
            batch_size=32,
            class_mode='categorical'
        )

        print(f"Predict using the model : {modelPath}")
        # Resize all images to a consistent size (64x64)
        # notations_resized = [tf.expand_dims(img, axis=-1) for img in notations_of_single_line]
        notationsResized = [cv2.resize(img, (64, 64)) for img in notationsOfSingleLine]

        # Convert to numpy array and normalize pixel values
        notationsArrayResized = np.array(notationsResized) / 255.0

        # Make predictions
        predictions = cnn.predict(notationsArrayResized)

        # Get the predicted class indices
        predictedClassIndices = np.argmax(predictions, axis=1)

        # Assuming you have a mapping of class indices to class labels
        classLabels = list(trainingSet.class_indices.keys())

        # Get the predicted class labels
        predictedClassLabels = [classLabels[index] for index in predictedClassIndices]

        # print("Predicted Class Labels:", predicted_class_labels)

        return predictedClassLabels
    
    