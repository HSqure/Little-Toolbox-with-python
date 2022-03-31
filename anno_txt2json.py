#coding=utf-8
'''
    convert old yolov3 coco/annotations .txt file to fit this version
'''

import xml.etree.ElementTree as ET
from PIL import Image
from pathlib import Path
import numpy as np
import json
import glob

# Category
PRE_DEFINE_CATEGORIES = {"person": 1, 
                         "bicycle": 2, 
                         "car": 3, 
                         "dog": 4}

JSON_NAME = 'thermal_annotations_train.json'
JPEGIMAGES_FOLDER = 'thermal_8_bit'

PORJ_PATH = '/home/huahua/Workspace/Pyotrch/pytorch-yolo3-thermal'
DATASET_PATH = '/home/huahua/Workspace/dataset/FLIR_ADAS_1_3/train'
# 需要转换的.txt文件名与路径
TRAIN_LIST_NAME = '/home/huahua/Workspace/Tensorflow/keras-yolo3-thermal/thermal_train.txt'

VAL_NUM = 500

'''
    创建文件夹
'''
def create_folder(folder_name):
    import os
    # take the part before '.' as folder name, which is video name
    # folder_name = video_name.split('.')[0]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print('--- Creating new folder{}... ---'.format(folder_name))
    # else:
        # print('--- Using existed folder ---')
    # return folder_name

'''
    从生成的yolo训练所需的annotation文本文件中提取bbox
'''
def load_anno_txt(path):
    # 读取并存放全部annotation文本内容,以换行符为flag进行分行
    annotation_set = open(path).read().split('\n')
    dataset = []
    img_id = 1
    box_id = 1
    # 创建coco标注文件夹
    create_folder(DATASET_PATH+'/coco/annotations')
    # 创建.json标注文件
    json_fp = open(DATASET_PATH+'/coco/annotations'+'/'+JSON_NAME, 'w')
    # ------------- [1].整体JSON文件格式 ---------------
    json_dict = {"info":{"year": 2019, 
                         "version": "1.0", 
                         "description": "For object detection", 
                         "date_created": "2022"},
                 "images":[], 
                 "type": "instances", 
                 "annotations": [],
                 "categories": []}    
    categories = PRE_DEFINE_CATEGORIES


    # ------------- [2].annotations字段 ---------------
    for annotation_line in annotation_set:
        is_val=0
        if len(annotation_line)==0:
            continue
        # 剥离后缀,剥离后分为两段: 第1段为图片路径(缺个后缀), 第2段为该图片中的所有box的组
        line = annotation_line.strip('\n')
        pic_format = line.split('.')[1].split(' ')[0] # 取出后缀名
        line = line.split(pic_format)

        ''' 以下为对无标注box图像(用于样本均衡)的适应性判断 '''
        # 如果line有两个元素(图片地址与bbox),则说明有bbox
        # 否则该图片没有bbox标注
        if np.size(line)==2:
            
            # 添加回后缀读取第1段的图片文件,获取图片名
            pic_name = Path(line[0]+pic_format).name

            # 将数据集分为train和al两个部分
            if img_id <= VAL_NUM: # val
                is_val=1
                pic_path = str(Path(line[0]+pic_format).parents[0])+'/'+pic_name
                # val_list.write(pic_path+'\n')
                # # 以每张图为对应创建.txt标注val文件
                # lable_txt_file_val = open(DATASET_PATH+'/coco/annotations/'
                #                           +Path(line[0]+'txt').name,'w')
            else: # train
                is_val=0
                pic_path = str(Path(line[0]+pic_format).parents[0])+'/'+pic_name
                # train_list.write(pic_path+'\n')
                # # 以每张图为对应创建.txt标注train文件
                # lable_txt_file_train = open(DATASET_PATH+'/coco/annotations/'
                #                             +(Path(line[0]+'txt').name),'w')
            
            image = Image.open(pic_path)
            width, height = image.size
            # print('Porccessing picture: {} | width: {} Height: {}'.format(pic_path, width, height))
            print('id: {} | file_name: {} | width: {} Height: {}'.format(img_id, pic_name, width, height))

            image = {'file_name': JPEGIMAGES_FOLDER + '/' + pic_name, 
                     'height': height, 
                     'width': width,
                     'id':img_id}

            json_dict['images'].append(image)
            
            # 将第2段的多个以空格分隔的box组分割后，把得到的每个box存放在list型的box_set中
            box_set = line[1].split(' ')
            # 开始解析每个box的坐标数据 
            for box in box_set:
                if len(box)==0:
                    continue
                # 每个box_axis包含box的5个信息:
                # xmin, ymin, xmax, ymax, category = box_axis[0], box_axis[1], box_axis[2], box_axis[3], box_axis[4]
                box_axis = box.split(',')
                xmin = np.float64(int(box_axis[0]) / width)
                ymin = np.float64(int(box_axis[1]) / height)
                xmax = np.float64(int(box_axis[2]) / width)
                ymax = np.float64(int(box_axis[3]) / height)

                box_class = box_axis[4]
                x_center = (xmin+xmax)/2
                y_center = (ymin+ymax)/2
                box_w = xmax-xmin
                box_h = ymax-ymin
         
                if xmax == xmin or ymax == ymin:
                    print('Error box in Image File: {}'.format(str(line[0]+pic_format)))

                ann = { 'image_id': img_id, 
                        'bbox':[xmin, ymin, box_w, box_h],
                        'category_id': box_class, 
                        'id': box_id, 
                        'segmentation': []}

                json_dict['annotations'].append(ann)
                box_id+=1
            #     if is_val:
            #         lable_txt_file_val.write('{} {} {} {} {}\n'.format(box_class,x_center,y_center,box_w,box_h))
            #     else:
            #         lable_txt_file_train.write('{} {} {} {} {}\n'.format(box_class,x_center,y_center,box_w,box_h))

            # if is_val:
            #     lable_txt_file_val.close()
            # else:
            #     lable_txt_file_train.close()
            img_id+=1
        # ------------- [3].categories字段 ---------------

    for cate, cid in categories.items():
        cat = { 'supercategory': 'unknown', 
                'id': cid, 
                'name': cate}
        json_dict['categories'].append(cat)
    # train_list.close()
    # train_list.close()
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()

    # return np.array(dataset)


# 主程序
if __name__ == '__main__':
    
    # 加载标注box的文件
    anno_data = load_anno_txt(TRAIN_LIST_NAME)
    
