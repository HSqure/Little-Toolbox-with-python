# coding=utf-8

"""
    将coco数据集信息导入自己的annotation文件(.txt)
"""

TRAIN_PATH = '/home/huahua/Workspace/dataset/TACO-trash-dataset/data/'
TRAIN_JSON_FILE_NAME = 'annotations.json'
PIC_PATH = TRAIN_PATH

LIST_FILE_PATH = 'model_data/'
LIST_FILE_NAME = 'coco_classes_trash.txt'


import json
import numpy as np
from collections import defaultdict
from os import getcwd

#def convert_annotation(image_id, json_file_data, list_file):

def cat_fix(catagory_id):
    #if catagory_id 

    return catagory_id - 1

def read_anno_from_coco_json(list_file):
    # 打开.json标注文件
    f = open(
        TRAIN_PATH + TRAIN_JSON_FILE_NAME,
        encoding='utf-8')

    # 将文件所有信息保存在data中
    data = json.load(f)

    # 从data中提取信息
    categories = data['categories'] # 类别信息

    # 初始化
    cate_buff=''
    cate_id=0

    for category in categories:
        # 类别查重
        if not (cate_buff == category['supercategory']): # 如果类别名跟上次出现的不一样的,才增发新的重新编码的id号
            cate_id = cate_id + 1
            # list_file.write(str(category['supercategory']) +':'+ str(category['id'])+'\n')
            list_file.write(str(category['supercategory']) +'\n')
        cate_buff=category['supercategory']
        
    f.close()



if __name__ == '__main__':

    list_file = open(LIST_FILE_PATH+LIST_FILE_NAME, 'w')

    read_anno_from_coco_json(list_file)

    list_file.close()
