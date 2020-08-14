import cv2
import numpy as np
from keras.models import model_from_json
import glob
from .local_utils import detect_lp
from os.path import splitext, basename
from statistics import median
import os
from sklearn.preprocessing import LabelEncoder

def draw_box_img(vehicle_image, cor, thickness=3, cornum=0,L=[]): 
    pts=[]  
    x_coordinates=cor[cornum][0]
    y_coordinates=cor[cornum][1]
    # store the top-left, top-right, bottom-left, bottom-right 
    # of the plate license respectively
    for i in range(4):
        pts.append([int(x_coordinates[i]),int(y_coordinates[i])])
    
    pts = np.array(pts, np.int32)
    pts = pts.reshape((-1,1,2))
    if len(L)==0 or L[cornum]>0.80 : color = (0,255,0)
    else: color = (225,0,100)
    cv2.polylines(vehicle_image,[pts],True,color,thickness)
    return vehicle_image

def load_model(path):
    try:
        path = splitext(path)[0]
        with open('%s.json' % path, 'r') as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights('%s.h5' % path)
        print("Loading model successfully...")
        return model
    except Exception as e:
        print(e)

def preprocess_image(image_path,resize=False):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255
    if resize:
        img = cv2.resize(img, (224,224))
    return img

def get_plate(image_path, Dmax=608, Dmin=256,wpod_net =[]):
    #print('----------------------- in get_plate')
    vehicle = preprocess_image(image_path)
    ratio = float(max(vehicle.shape[:2])) / min(vehicle.shape[:2])
    side = int(ratio * Dmin)
    bound_dim = min(side, Dmax)
    LpImg=[]
    L=[]
    #_ , LpImg, _, cor = detect_lp(wpod_net, vehicle, bound_dim, lp_threshold=0.5)
    L, LpImg, lp_type, cor = detect_lp(wpod_net, vehicle, bound_dim, lp_threshold=0.5)
    # print('--------------------')
    # print("Detect %i plate(s) in"%len(LpImg),os.path.split(image_path)[1])
    # #print("Coordinate of plate(s) in image: \n", cor)
    # if (len(L)>0):print("Max Probability of a plate [0]: ", L[0])

    return LpImg, cor, [x.prob() for x in L]

# def draw_box_img(vehicle_image, cor, thickness=3, cornum=0,L=[]): 
#     pts=[]  
#     x_coordinates=cor[cornum][0]
#     y_coordinates=cor[cornum][1]
#     # store the top-left, top-right, bottom-left, bottom-right 
#     # of the plate license respectively
#     for i in range(4):
#         pts.append([int(x_coordinates[i]),int(y_coordinates[i])])
    
#     pts = np.array(pts, np.int32)
#     pts = pts.reshape((-1,1,2))
#     if len(L)==0 or L[cornum]>0.80 : color = (0,255,0)
#     else: color = (225,0,100)
#     cv2.polylines(vehicle_image,[pts],True,color,thickness)
#     return vehicle_image

def make_boxes(LpImg):
    plate_image= cv2.convertScaleAbs(LpImg[0], alpha=(255.0))
    test_roi = plate_image.copy()
    # convert to grayscale and blur the image
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(7,7),0)
    # Applied inversed thresh_binary 
    binary = cv2.threshold(blur, 140, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    crop_characters = []
    crop_characters_orig=[]
    cont=[]

    maxh=plate_image.shape[0]
    maxw=plate_image.shape[1]
    minw=maxw/30
    minh=maxh/5

    cont, _  = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marginh=0
    marginw=0
    if(len(cont)==1):
        print('havent found any characters -  cutting margings')
        m=0.05
        marginh=round(m*maxh)
        marginw=round(m*maxw)
        cut_plate_image=plate_image[marginh:maxh-marginh,marginw:maxw-marginw]
        cut_binary=binary[marginh:maxh-marginh,marginw:maxw-marginw]
        cont, _  = cv2.findContours(cut_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        test_roi = cut_plate_image.copy()
    
    # if finding contours worked the first time, margins=0 and cut_images are equal uncut ones
    cut_plate_image=plate_image[marginh:maxh-marginh,marginw:maxw-marginw]
    cut_binary=binary[marginh:maxh-marginh,marginw:maxw-marginw]
    

    bb=[cv2.boundingRect(c) for c in cont]
    a=np.array(bb)
    a1=a[a[:,2]>=minw]
    a2=a1[a1[:,3]>=minh]

    hmedian=median(a2[:,3])
    wmedian=median(a2[:,2])

    a3=a2[abs(a2[:,3]-hmedian)/hmedian<0.3]
    a4=a3[a3[:,0].argsort()]

    if(hmedian<maxh/3):
        print('multiple lines')
        a4=a3[(a3[:,0]+(a3[:,1]//minh*10*minh)).argsort()]

    myboxes=a4


    idx=0
    digit_w, digit_h = 30, 60
    for i in range(len(myboxes)):
        #x=bb[i][0]
        x, y, w, h = myboxes[i]
        if h/plate_image.shape[0]>=0.3 and w/plate_image.shape[0]<0.9 :
            cv2.rectangle(test_roi, (x, y), (x + w, y + h), (0, 200,0), 2)
            cv2.putText(test_roi, str(idx), (x+10, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,210,0), 2)
            idx=idx+1
            
            # extract the img
            curr_num = cut_binary[y:y+h,x:x+w]
            curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
            _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            curr_num_orig = cut_plate_image[y:y+h,x:x+w]
            crop_characters.append(curr_num) 
            crop_characters_orig.append(curr_num_orig)


    return(test_roi, myboxes, crop_characters, crop_characters_orig)

def predict_from_model(image,model,labels):
    image = cv2.resize(image,(80,80))
    image = np.stack((image,)*3, axis=-1)
    prediction = labels.inverse_transform([np.argmax(model.predict(image[np.newaxis,:]))])
    return prediction