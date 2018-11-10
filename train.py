import argparse
import os

import numpy as np
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.optimizers import SGD, Adam

from config import alpr_config as config
from licence_plate_dataset_generator import LicensePlateDatasetGenerator
from pyimagesearch.callbacks import CustomModelCheckpoint
from pyimagesearch.io.hdf5datasetloader import Hdf5DatasetLoader
from pyimagesearch.nn.conv import OCR

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", default=config.MODEL_PATH, help="model file")
ap.add_argument("-k", "--folds", default=config.FOLDS, type=int, help="k-folds")
ap.add_argument("-o", "--optimizer", default="sdg", help="optimizer method: sdg, adam, rmprop")
args = vars(ap.parse_args())

k = args['folds']


def get_optimizer(optimizer_method):
    if optimizer_method == "sdg":
        return SGD(lr=1e-2, decay=1e-6, momentum=0.9, nesterov=True, clipnorm=5)
    if optimizer_method == "adam":
        return Adam(lr=0.001, decay=0.001 / config.NUM_EPOCHS)


def create_model(img_w, img_h, pool_size, output_size, max_text_length, optimizer_method):
    model = OCR.build(img_w, img_h, pool_size, output_size, max_text_length)
    model.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer=get_optimizer(optimizer_method))
    return model


def get_callbacks(output_path, optimizer_method, fold_index, model_name):
    # construct the set of callbacks
    # callbacks = [
    #     EpochCheckpoint(config.CHECKPOINTS_PATH, every=5, startAt=config.START_EPOCH),
    #     TrainingMonitor(config.FIG_PATH, jsonPath=config.JSON_PATH, startAt=config.START_EPOCH)]

    model_checkpoint_path = os.path.sep.join(
        [output_path, optimizer_method, "fold{:02d}".format(fold_index), model_name]) + '.{epoch:02d}.h5'

    callbacks = [
        EarlyStopping(monitor='loss', min_delta=0.01, patience=5, mode='min', verbose=1),
        CustomModelCheckpoint(model_to_save=model, filepath=model_checkpoint_path,
                              monitor='loss', verbose=1, save_best_only=True, mode='min', period=1),
        ReduceLROnPlateau(monitor='loss', factor=0.1, patience=2, verbose=1, mode='min', min_delta=0.01,
                          cooldown=0, min_lr=0)]
    return callbacks


print("[INFO] loading data...")
loader = Hdf5DatasetLoader()
images, labels = loader.load(config.TRAIN_HDF5, shuffle=True)
fold_size = int(len(images) / k)
cvscores = []

for fold_index in range(k):
    val_data = images[fold_index * fold_size:(fold_index + 1) * fold_size]
    val_labels = labels[fold_index * fold_size:(fold_index + 1) * fold_size]

    train_data = np.concatenate([images[:fold_index * fold_size], images[(fold_index + 1) * fold_size:]])
    train_labels = np.concatenate([labels[:fold_index * fold_size], labels[(fold_index + 1) * fold_size:]])

    print("Training on fold " + str(fold_index + 1) + "/{0}...".format(k))

    trainGen = LicensePlateDatasetGenerator(train_data, train_labels, config.IMAGE_WIDTH, config.IMAGE_HEIGHT,
                                            config.POOL_SIZE, config.MAX_TEXT_LEN, config.BATCH_SIZE,
                                            config.SUN397_HDF5)

    valGen = LicensePlateDatasetGenerator(val_data, val_labels, config.IMAGE_WIDTH, config.IMAGE_HEIGHT,
                                          config.POOL_SIZE, config.MAX_TEXT_LEN, config.BATCH_SIZE, config.SUN397_HDF5)

    model = create_model(config.IMAGE_WIDTH, config.IMAGE_HEIGHT, config.POOL_SIZE,
                         trainGen.get_output_size(), config.MAX_TEXT_LEN, args['optimizer'])

    history = model.fit_generator(
        trainGen.generator(),
        steps_per_epoch=trainGen.numImages // config.BATCH_SIZE,
        validation_data=valGen.generator(),
        validation_steps=valGen.numImages // config.BATCH_SIZE,
        epochs=config.NUM_EPOCHS,
        max_queue_size=10,
        callbacks=get_callbacks(config.OUTPUT_PATH, args['optimizer'], fold_index, config.MODEL_NAME),
        verbose=1)

    # scores = model.evaluate(val_data, val_labels, verbose=1)
    # print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))
    # cvscores.append(scores[1] * 100)

    accuracy_history = history.history['acc']
    val_accuracy_history = history.history['val_acc']
    print("Last training accuracy: " + str(accuracy_history[-1]) + ", last validation accuracy: " + str(
        val_accuracy_history[-1]))

print("{:.2f}%% (+/- {:.2f}%%)".format(np.mean(cvscores), np.std(cvscores)))
