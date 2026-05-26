import keras
import tensorflow as tf
from keras.callbacks import TensorBoard
from keras.preprocessing.image import ImageDataGenerator

tf.__version__

# Data pre-processing

# 1.Pre-processing training set
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

# Pre-processing test set
training_set = train_datagen.flow_from_directory(
    'train_data/MuscimaRefined',
    target_size=(64, 64),
    batch_size=32,
    class_mode='categorical'
)

# 2.Building the CNN

# Initializing the CNN
cnn = keras.models.Sequential()

# Convolution
cnn.add(
    keras.layers.Conv2D(
        filters=32,
        kernel_size=3,
        activation='relu',
        input_shape=(64, 64, 3))
)

# Pooling
#cnn.add(keras.layers.MaxPool2D(pool_size=2, strides=2))

# Adding a second convolution layer
cnn.add(
    keras.layers.Conv2D(
        filters=64,
        kernel_size=3,
        activation='relu')
)
# Pooling
cnn.add(keras.layers.MaxPool2D(pool_size=2, strides=2))

# Adding a third convolution layer
cnn.add(
    keras.layers.Conv2D(
        filters=64,
        kernel_size=3,
        activation='relu')
)
# Pooling
cnn.add(keras.layers.MaxPool2D(pool_size=2, strides=2))

# Adding a fourth convolution layer
cnn.add(
    keras.layers.Conv2D(
        filters=64,
        kernel_size=3,
        activation='relu')
)
# Pooling
#cnn.add(keras.layers.MaxPool2D(pool_size=2, strides=2))


# Flattening
cnn.add(keras.layers.Flatten())

# Full Connection
cnn.add(keras.layers.Dense(units=128, activation='relu'))

# Output Layer
cnn.add(keras.layers.Dense(units=len(training_set.class_indices), activation='softmax'))

# 3.Training the CNN

# Compiling the CNN
cnn.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'])

# Initialize TensorBoard callback
tensorboard_callback = TensorBoard(
    log_dir='./logs',
    histogram_freq=1)

# Training the CNN on the training set and evaluating it on the Test set
cnn.fit(
    x=training_set,
    epochs=25, # 25
    callbacks=[tensorboard_callback])

cnn.summary()

cnn.save('trained_models/cnn_trained_model_modified.h5')
