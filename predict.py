import argparse
import os

import cv2
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.models import load_model

from config import config
from label_codec import LabelCodec
from pyimagesearch.preprocessing import AspectAwarePreprocessor

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default="DÜW-AS870.jpg", type=str, help="image to predict")
ap.add_argument("-l", "--label", default="DÜW-AS870", type=str, help="true label")
ap.add_argument("-o", "--optimizer", default=config.OPTIMIZER, help="supported optimizer methods: sdg, rmsprop, adam, adagrad, adadelta")
args = vars(ap.parse_args())

MODEL_PATH = os.path.join(config.OUTPUT_PATH, args["optimizer"], config.MODEL_NAME) + ".h5"
print("Model path:   {}".format(MODEL_PATH))

img_filepath = os.path.join(config.TEST_IMAGES, args["image"])
label = args["label"]
print("Image: {}".format(img_filepath))
print("Label: {}".format(label))

tf.compat.v1.disable_eager_execution()


def load_image(filepath):
    stream = open(filepath, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    image = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)

    # convert image to grayscale, if it is not already a grayscale image
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return image


model = load_model(MODEL_PATH, compile=False)

aap = AspectAwarePreprocessor(config.IMAGE_WIDTH, config.IMAGE_HEIGHT)

image = Image.open(img_filepath)
image = aap.preprocess(image)
image = image.astype(np.float32) / 255.
image = np.expand_dims(image.T, -1)

predictions = model.predict(np.asarray([image]))
pred_number = LabelCodec.decode_prediction(predictions[0])
fig = plt.figure(figsize=(15, 10))
outer = gridspec.GridSpec(1, 2, wspace=0.5, hspace=0.1)
ax1 = plt.Subplot(fig, outer[0])
fig.add_subplot(ax1)
print('Predicted: %9s\nTrue:      %9s\n=> %s' % (pred_number, label, pred_number == label))
image = image[:, :, 0].T
ax1.set_title('True: {}\nPred: {}'.format(label, pred_number), loc='left')
ax1.imshow(image, cmap='gray')
ax1.set_xticks([])
ax1.set_yticks([])

ax2 = plt.Subplot(fig, outer[1])
fig.add_subplot(ax2)
ax2.set_title('Activations')
ax2.imshow(predictions[0].T, cmap='binary', interpolation='nearest')
ax2.set_yticks(list(range(len(LabelCodec.ALPHABET) + 1)))
ax2.set_yticklabels(LabelCodec.ALPHABET)  # + ['blank'])
ax2.grid(False)
for h in np.arange(-0.5, len(LabelCodec.ALPHABET) + 1 + 0.5, 1):
    ax2.axhline(h, linestyle='-', color='k', alpha=0.5, linewidth=1)

plt.show()
