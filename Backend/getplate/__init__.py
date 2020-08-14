import logging

import azure.functions as func

import os
import cv2
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
import glob
#from read_plate import *
import sys

from .helper import * 

wpod_net = []
labels = []
model = []

def _initialize():
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
        logging.info("[INFO] Model loaded successfully...")

        labels = LabelEncoder()
        labels.classes_ = np.load(Classes_filename)
        logging.info("[INFO] Labels loaded successfully...")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    _initialize()
  
    id = 14
    id_str = req.params.get('id')
    if id_str:  
        id = int(id_str)

    # --------------------------- get data for ocr
    scriptpath = os.path.abspath(__file__)
    scriptdir = os.path.dirname(scriptpath)
    data_path = os.path.join(scriptdir, '../data/')
    image_paths = glob.glob(data_path + "/*.jpg")

    test_image = image_paths[id]
    # --------------------------- get plate
    LpImg, cor, L =get_plate(test_image,wpod_net=wpod_net)
    # --------------------------- extract characters
    test_roi, myboxes, crop_characters, crop_characters_orig = make_boxes(LpImg)
    # --------------------------- read characters
    final_string = ''
    for i,character in enumerate(crop_characters): 
        char=np.array2string(predict_from_model(character,model,labels))
        final_string+=char.strip("'[]")

    print(final_string)

    return func.HttpResponse(final_string)
    
    # name = req.params.get('name')
    # if not name:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         name = req_body.get('name')

    # if name:
    #     return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    # else:
    #     return func.HttpResponse(
    #          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #          status_code=200
    #     )
