import logging

import azure.functions as func

import io
import os
import sys
import cv2
import numpy as np
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
import glob

from .helper import * 

# global variables used for model caching
wpod_net = []
labels = []
model = []

def _initialize():
    # load all models and chace in global variables
    global labels, wpod_net, model
    if not labels:
        scriptpath = os.path.abspath(__file__)
        scriptdir = os.path.dirname(scriptpath)
        model_path = os.path.join(scriptdir, 'wpod-net.json')
        MobileNets_filename = os.path.join(scriptdir, 'MobileNets_character_recognition.json')
        Weights_filename = os.path.join(scriptdir, 'License_character_recognition_weight.h5')
        Classes_filename = os.path.join(scriptdir, 'license_character_classes.npy')

        # Load model for plate detection
        wpod_net = load_model(model_path)

        # -------------------- Load model architecture, weight and labels
        json_file = open(MobileNets_filename, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights(Weights_filename)
        logging.info("Model loaded successfully...")

        labels = LabelEncoder()
        labels.classes_ = np.load(Classes_filename)
        logging.info("Labels loaded successfully...")

#def main(req: func.HttpRequest) -> func.HttpResponse:
def main(req: func.HttpRequest, fullpicture: func.Out[bytes], cutplate: func.Out[bytes],) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    _initialize()

    body = req.get_body()
    image = np.fromstring(body, np.uint8)
    
    # --------------------------- get plate
    LpImg, cor, L =get_plate(image, wpod_net=wpod_net)

    # --------------------------- extract characters
    test_roi, myboxes, crop_characters, crop_characters_orig = make_boxes(LpImg)
    
    # --------------------------- read characters
    final_string = ''
    for i,character in enumerate(crop_characters): 
        char=np.array2string(predict_from_model(character,model,labels))
        final_string+=char.strip("'[]")

    # following an example https://github.com/yokawasa/azure-functions-python-samples/tree/master/v2functions/blob-trigger-watermark-blob-out-binding
    #img_byte_arr = io.BytesIO()
    # Convert composite to RGB so we can save as JPEG
    #image.convert('RGB').save(img_byte_arr, format='JPEG')
    #blobout.set(img_byte_arr.getvalue())

    fullpicture.set(body)

    frame = LpImg[0]
    frame = frame[:, :, [2, 1, 0]]
    frame = 255*frame

    _, encoded_image = cv2.imencode('.jpg', frame)
    encoded_bytes = encoded_image.tobytes()
    
    cutplate.set(encoded_bytes)

    return func.HttpResponse(final_string)