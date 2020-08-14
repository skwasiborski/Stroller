import os
import cv2
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
import glob
#from read_plate import *
from helper import * 

print(os.getcwd())
os.chdir('./code')
image_paths = glob.glob("../data/*.jpg")

# Load model for plate detection
model_path=os.path.join(os.getcwd(),"wpod-net.json")
wpod_net = load_model(model_path)

# -------------------- Load model architecture, weight and labels
json_file = open('MobileNets_character_recognition.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
model.load_weights("License_character_recognition_weight.h5")
print("[INFO] Model loaded successfully...")

labels = LabelEncoder()
labels.classes_ = np.load('license_character_classes.npy')
print("[INFO] Labels loaded successfully...")

# --------------------------- get data for ocr
test_image = image_paths[14]
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
