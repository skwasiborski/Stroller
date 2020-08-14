
import os


import cv2
import numpy as np
import matplotlib.pyplot as plt
from local_utils import detect_lp
from os.path import splitext, basename
from keras.models import model_from_json
import glob
import matplotlib.gridspec as gridspec
from sklearn.preprocessing import LabelEncoder
from helper import *

#img_path='Plate_detect_and_recognize/Plate_examples\\16-204476.jpg'

def read_plate(img_path, plate_model):
    LpImg=[]
    cor=[]
    L=[]
    binary=[]
    respath='ERROR'
    try:
        LpImg,cor,L = get_plate(img_path, wpod_net = plate_model)
        print('--------------------')
        print("Detect %i plate(s) in"%len(LpImg),os.path.split(img_path)[1])
        #print("Coordinate of plate(s) in image: \n", cor)
        print("Max Probability of a plate [0]: ", L[0])

 
        # plt.title('Probability of this licence plate :  '+str(L[0]))
        # plt.axis(False)
        # plt.imshow(LpImg[0])
        # resname=os.path.split(img_path)[1]
        # resname=os.path.splitext(resname)[0]
        # respath=os.path.join('results','Extracted','EXTRACTED_'+resname+'PNG')
        # print('----------------------')
        # print('  saving  '+ respath)

        # plt.savefig(respath, dpi=400)

        # plate_image = cv2.convertScaleAbs(LpImg[0], alpha=(255.0))
        
        # # convert to grayscale and blur the image
        # gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        # blur = cv2.GaussianBlur(gray,(7,7),0)
        # # Applied inversed thresh_binary 
        # binary = cv2.threshold(blur, 180, 255,
        #                     cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # thre_mor = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel3)

        # plt.imshow(binary,cmap="gray")
        # resname=os.path.split(img_path)[1]
        # resname=os.path.splitext(resname)[0]
        # respath=os.path.join('results','Binary','BINARY_'+resname)
        # print('----------------------')
        # print('  saving  '+ respath)

        # plt.savefig(respath, dpi=400)
    except: pass
    return(LpImg, cor, L)


# model_path=os.path.join('Plate_detect_and_recognize',"wpod-net.json")
# wpod_net = load_model(model_path)
# LpImg, cor, L =read_plate(img_path,wpod_net)

