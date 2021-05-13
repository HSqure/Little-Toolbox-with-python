# coding=utf-8

"""
    将coco数据集信息导入自己的annotation文件(.txt)
"""

TRAIN_PATH = '/home/huahua/Workspace/dataset/Brackish_Dataset/'
TRAIN_JSON_FILE_NAME = 'annotations/annotations_COCO/train_groundtruth.json'
PIC_PATH = TRAIN_PATH + 'dataset/Images/'

LIST_FILE_PATH = './'
LIST_FILE_NAME = 'fish_train.txt'


import json
import numpy as np
from collections import defaultdict
from os import getcwd

#def convert_annotation(image_id, json_file_data, list_file):

def cat_fix(catagory_id):
    # 如果种类id为17,则将其转换为4
    return catagory_id - 1

def read_anno_from_coco_json(list_file):
    # 打开.json标注文件
    f = open(
        TRAIN_PATH + TRAIN_JSON_FILE_NAME,
        encoding='utf-8')

    # 将文件所有信息保存在data中
    data = json.load(f)

    # 从data中提取信息
    #category_index = data['categories'] # 全部类别索引
    image_info = data['images'] # 图片信息
    anno = data['annotations'] # 标注信息

    for info in image_info:
        has_gtbox = False # gt_box存在指示器初始化
        gt_box = ' ' # 如果没有gt_box,则初始化为一个空格
        pic_id = info['id'] # 取当前pic_id,在下面的循环中找到与其匹配的segmentation,即gt_box的坐标
        file_name = info['file_name']
        pic_location = PIC_PATH + str(file_name)

        for gt in anno:
            # 查找同一图片下的所有gt_box (image_id为json对训练集图片的内部编号,与图片名无关)
            if gt['image_id'] == pic_id:
                # 只执行一次初始化
                if has_gtbox==False: 
                    gt_box = ''
                    has_gtbox = True
                # 取bbox中的x,y,width,height并转换成xmin,ymin,xmax,ymax
                box_axis = ( 
                    str(gt['bbox'][0]) + ',' + 
                    str(gt['bbox'][1]) + ',' + 
                    str(gt['bbox'][0]+gt['bbox'][2]) + ',' + 
                    str(gt['bbox'][1]+gt['bbox'][3])
                )
                box_category = cat_fix(gt['category_id']) # 数据集类别id修正
                # 整合累加
                gt_box = str(gt_box) + ' ' + str(box_axis) + ',' + str(box_category)
                print( 'proccessing {0:.2f}% completed'.format((pic_id/9967)*100))

        # 将"图片路径"与"annotation信息"写入到.txt文件中
        list_file.write(pic_location + str(gt_box))
        list_file.write('\n')

    f.close()



if __name__ == '__main__':

    list_file = open(LIST_FILE_PATH+LIST_FILE_NAME, 'w')

    read_anno_from_coco_json(list_file)

    list_file.close()
