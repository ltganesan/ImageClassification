'''In our setup, we:
- created a data/ folder
- created train/ and validation/ subfolders inside data/
- created cats/ and dogs/ subfolders inside train/ and validation/
- put the cat pictures index 1-1024 in data/train/cats
- put the cat pictures index 1025-1440 in data/validation/cats
- put the dogs pictures index 1-1024 in data/train/dogs
- put the dog pictures index 1025-1440 in data/validation/dogs
So that we have 1024 training examples for each class, and 416 validation examples for each class.
In summary, this is our directory structure:
```
data/
    train/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
    validation/
        dogs/
            dog1025.jpg
            dog1026.jpg
            ...
        cats/
            cat1025.jpg
            cat1026.jpg
            ...
```
'''
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense
from keras import applications

# dimensions of our images.
img_width, img_height = 150, 150

top_model_weights_path = 'top_model.h5'
train_data_dir = 'data/train'
validation_data_dir = 'data/validation'
nb_train_samples = 2048
nb_validation_samples = 832
epochs = 50
batch_size = 16


def save_features():

    datagen = ImageDataGenerator(rescale=1. / 255)

    # build the VGG16 network
    model = applications.VGG16(include_top=False, weights='imagenet')

    generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    features_train = model.predict_generator(
        generator, nb_train_samples // batch_size)
    np.save(open('features_train.npy', 'wb'), features_train)

    generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    features_validation = model.predict_generator(
        generator, nb_validation_samples // batch_size)
    np.save(open('features_validation.npy', 'wb'), features_validation)


def train_top_model():
    train_data = np.load(open('features_train.npy', 'rb'))
    train_labels = np.array([0] * (nb_train_samples // 2) + [1] * (nb_train_samples // 2))

    validation_data = np.load(open('features_validation.npy', 'rb'))
    validation_labels = np.array([0] * (nb_validation_samples // 2) + [1] * (nb_validation_samples // 2))
    model_top = Sequential()
    model_top.add(Flatten(input_shape=train_data.shape[1:]))
    model_top.add(Dense(256, activation='relu'))
    model_top.add(Dropout(0.5))
    model_top.add(Dense(1, activation='sigmoid'))

    model_top.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

    model_top.fit(train_data, train_labels,
                  epochs=epochs,
                  batch_size=batch_size,
                  validation_data=(validation_data, validation_labels))

    model_top.save_weights(top_model_weights_path)
    model_top.evaluate(validation_data, validation_labels)

save_features()
train_top_model()
