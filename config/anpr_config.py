# import the necessary packages
from os import path

IMAGE_WIDTH = 160
IMAGE_HEIGHT = 32

# initialize the batch size and number of epochs for training
BATCH_SIZE = 128
POOL_SIZE = 2
NUM_EPOCHS = 50
START_EPOCH = 0

MAX_TEXT_LEN = 9
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ0123456789- "

MODEL_NAME = "anpr.model"

# json file with the list of german county marks
GERMAN_COUNTY_MARKS = "./config/german_county_marks.json"

DATASET_PATH = "../datasets"
# define the paths to the training and validation directories
TRAIN_IMAGES = path.sep.join([DATASET_PATH, "anpr/images"])
VAL_IMAGES = path.sep.join([DATASET_PATH, "anpr/val"])

# define the path to the output training, validation, and testing HDF5 files
TRAIN_HDF5 = path.sep.join([DATASET_PATH, "anpr/hdf5/train.h5"])
VAL_HDF5 = path.sep.join([DATASET_PATH, "anpr/hdf5/val.h5"])
TEST_HDF5 = path.sep.join([DATASET_PATH, "anpr/hdf5/test.h5"])

# define the path to the output directory used for storing plots,
# classification reports, etc.
OUTPUT_PATH = "output"
# path to the output model file
MODEL_PATH = path.sep.join([OUTPUT_PATH, MODEL_NAME]) + ".h5"
MODEL_CHECKPOINT_PATH = path.sep.join([OUTPUT_PATH, MODEL_NAME]) + '.{epoch:02d}.h5'
FIG_PATH = path.sep.join([OUTPUT_PATH, "anpr.png"])
JSON_PATH = path.sep.join([OUTPUT_PATH, "anpr.json"])
CHECKPOINTS_PATH = path.sep.join([OUTPUT_PATH, "checkpoints"])
TENSORBOARD_PATH = path.sep.join([OUTPUT_PATH, "tensorboard"])
