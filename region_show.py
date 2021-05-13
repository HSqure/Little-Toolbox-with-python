import numpy as np
import mat4py as mat
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import xml.etree.ElementTree as ET

import colorsys
import cv2
import random

# 目标种类字典
CATEGORY_DICT = {0:'apple', 
                 1:'damaged_apple'}

# DATASET_PATH = '/home/huahua/Workspace/Tensorflow/keras-yolo3-vehicle/dataset/UA-DETRAC2021/'
# XML_FILE = DATASET_PATH + 'Annotations/MVI_20011_v3.xml'
# IMG_PATH = DATASET_PATH + 'JPEGImages/MVI_20011/' + 'img00001.jpg'

# DATASET_PATH = '/home/huahua/Workspace/dataset/Brackish_Dataset/'
# IMG_PATH = TRAIN_PATH + 'dataset/Images/'
IMG_PATH = '/home/huahua/Workspace/dataset/TACO-trash-dataset/data/batch_7/000056.JPG'

# def get_axis_form_xml(xml_file_name):

#     xml_file = open(xml_file_name)
#     tree=ET.parse(xml_file)
#     root = tree.getroot()

#     ignored_region = root.find('ignored_region')
#     box = ignored_region.findall('box')

#     NUM=6

#     height = box[NUM].get('height')
#     left = box[NUM].get('left')
#     top = box[NUM].get('top')
#     width = box[NUM].get('width')

#     # for obj in root.iter('ignored_region'):
#     #     # for box in obj.iterfind('box'):
#     #     for box in obj.findall('box'):
#     #         # print(box.attrib['height'])
#     #         print(box.get('height'))

#     # print(height, left, top, width)

#     return float(height), float(left), float(top), float(width)

def draw(image, xmin, ymin, xmax, ymax, cat_num):
    category_name = CATEGORY_DICT
    image_h, image_w, _ = image.shape
    # 定义颜色
    hsv_tuples = [(1.0 * x / 6, 1., 1.) for x in range(6)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

    random.seed(0)
    random.shuffle(colors)
    random.seed(None)

    # ---------- 处理成非负整数 -----------------
    left = max(0, np.floor(xmin + 0.5).astype(int)) 
    top = max(0, np.floor(ymin + 0.5).astype(int)) 
    right = min(image.shape[1], np.floor(xmax + 0.5).astype(int))
    bottom = min(image.shape[0], np.floor(ymax + 0.5).astype(int))
    # ----------------------------------------
    bbox_color = colors[0]
    bbox_thick = 2
    cv2.rectangle(image, (left, top), (right, bottom), bbox_color, bbox_thick)
    t_size = cv2.getTextSize(category_name[cat_num], 0, 0.5, thickness=1)[0]
    cv2.rectangle(image, (left, top), (left + t_size[0], top - t_size[1] - 3), bbox_color, -1)
    cv2.putText(image, category_name[cat_num], (left, top - 2), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 0), 1, lineType=cv2.LINE_AA)

    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.imshow('img',image)
    cv2.waitKey (0)  
    cv2.destroyAllWindows() 

if __name__ == '__main__':

    img = cv2.imread(IMG_PATH) 

    # height, left, top, width = get_axis_form_xml(XML_FILE)
    # draw(img, xmin=left, ymin=top, xmax=left+width, ymax=top+height)

    draw(img, 850,1603,1014,1886,0)
