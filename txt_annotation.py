# coding=utf-8
from PIL import Image

"""
    将coco数据集信息导入自己的annotation文件(.txt)
"""

TRAIN_PATH = '/home/huahua/Workspace/dataset/PEDESTRIAN2021/'

PIC_PATH = TRAIN_PATH + 'JPEGImages/'
TRAIN_TXT_FILE_PATH = TRAIN_PATH + 'Annotations/' + 'train_bbox.txt'

TRAIN_JSON_FILE_NAME = 'annotations.json'

LIST_FILE_PATH = './'
LIST_FILE_NAME = 'pedestrian_train.txt'

PIC_FORMAT = '.jpg'

PIC_ID_TREASHOLD = 28000

import json
import numpy as np
from collections import defaultdict
from os import getcwd

# def convert_annotation(image_id, json_file_data, list_file):

def cat_fix(catagory_id):
    # 从成都开始
    return catagory_id - 1

# box格式转换
def xywh2xyminmax(gt_box):
    xmin = gt_box[0]
    ymin = gt_box[1]
    xmax = gt_box[0] + gt_box[2]
    ymax = gt_box[1] + gt_box[3]

    box_axis =( str(xmin) + ','
              + str(ymin) + ',' 
              + str(xmax) + ',' 
              + str(ymax))

    return box_axis

'''
    从生成的yolo训练所需的annotation文本文件中提取bbox
'''
def load_anno_txt(anno_txt_path, list_file):
    # 读取并存放全部annotation文本内容,以换行符为flag进行分行
    annotation_set = open(anno_txt_path).read().split('\n')
    dataset = []

    # 开始处理每一行
    for annotation_line in annotation_set:

        # 同时剥离'jpg'后缀+空格' ',剥离后分为两段: 第1段为图片路径(缺个后缀), 第2段为该图片中的所有box的组, 每个box以空格分隔
        line = annotation_line.strip('\n').split(PIC_FORMAT+' ') 

        '''以下为对无标注box图像(用于样本均衡)的适应性判断 '''
        # 如果查无'jpg'后缀,并且line有两个元素(图片地址与bbox),则说明上面已经将后缀剥离成功,说明有bbox
        # 否则剥离失败,该图片没有bbox标注(后缀后没有空格' ')
        if (line[0].find(PIC_FORMAT) == -1)&(np.size(line)==2):

            # ---------------------------- 根据图片名判断图片分属的文件夹 ----------------------------------
            name_key = 'sur'
            if name_key in line[0]:
                pic_location = PIC_PATH + 'su_01/' + line[0] + PIC_FORMAT
            else:
                # ============= 训练集阈值设置 ==============
                if (int(line[0].strip('ad')) >= PIC_ID_TREASHOLD):
                    break
                # =========================================

                if (int(line[0].strip('ad')) >= 10001)&(int(line[0].strip('ad')) <= 19999):
                    pic_location = PIC_PATH + 'ad_03/' + line[0] + PIC_FORMAT
                elif (int(line[0].strip('ad')) >= 20001)&(int(line[0].strip('ad')) <= 60179):
                    pic_location = PIC_PATH + 'ad_01/' + line[0] + PIC_FORMAT
                elif (int(line[0].strip('ad')) >= 60180)&(int(line[0].strip('ad')) <= 100000):
                    pic_location = PIC_PATH + 'ad_02/' + line[0] + PIC_FORMAT
                else:
                    print('picture number:{} out of range !'.format(str(line[0])))
            # -----------------------------------------------------------------------------------------
 
            image = Image.open(pic_location) # 添加回后缀,读取第1段的图片文件,验证图片路径是否正确
            width, height = image.size

            # 将第2段的多个以空格分隔的box组分割后，把得到的每个box存放在list型的box_set_per_line中
            box_set_per_line = line[1].split(' ')
            
            n=0
            gt_box=[0]*4 # 初始化列表
            gt_box_group=''
            
            for sub_num,box_element in enumerate(box_set_per_line):
                gt_box[n] = int(box_element)
                n = n + 1
                if ((sub_num+1)%4==0):
                    gt_box_group = gt_box_group + ' ' + xywh2xyminmax(gt_box) + ',0'
                    n=0

            list_file.write(pic_location + str(gt_box_group))
            list_file.write('\n')



if __name__ == '__main__':

    list_file = open(LIST_FILE_PATH+LIST_FILE_NAME, 'w')

    load_anno_txt(TRAIN_TXT_FILE_PATH,list_file)

    list_file.close()
