#coding=utf-8
'''
    convert old yolov3 annotations .txt file to fit this version
'''

import xml.etree.ElementTree as ET
from PIL import Image
from pathlib import Path
import numpy as np
import json
import glob

#ANNO_PATH = ''
PORJ_PATH = '/home/huahua/Workspace/Pyotrch/pytorch-yolo3-fish'
DATASET_LIST_PATH = '/home/huahua/Workspace/Pyotrch/pytorch-yolo3-fish/data/downloaded/fish'

DATASET_PATH = '/home/huahua/Workspace/dataset/Brackish_Dataset/dataset'

# 需要转换的.txt文件名与路径
TRAIN_LIST_NAME = '/home/huahua/Workspace/Tensorflow/keras-yolo3-fish/fish_train.txt'

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
    imgnum_cnt = 0
    create_folder(DATASET_LIST_PATH)
    create_folder(DATASET_PATH+'/pytorch_labels')
    # 创建.txt训练图片索引表
    train_list = open(DATASET_LIST_PATH+'/train.txt', 'w')
    # 创建.txt评估图片索引表
    val_list = open(DATASET_LIST_PATH+'/val.txt', 'w') 

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
            imgnum_cnt+=1
            # 添加回后缀读取第1段的图片文件,获取图片名
            pic_name = Path(line[0]+pic_format).name

            # 将数据集分为train和al两个部分
            if imgnum_cnt <= VAL_NUM: # val
                is_val=1
                pic_path = str(Path(line[0]+pic_format).parents[0])+'/'+pic_name
                val_list.write(pic_path+'\n')
                # 以每张图为对应创建.txt标注val文件
                lable_txt_file_val = open(DATASET_PATH+'/pytorch_labels/'
                                          +Path(line[0]+'txt').name,'w')
            else: # train
                is_val=0
                pic_path = str(Path(line[0]+pic_format).parents[0])+'/'+pic_name
                train_list.write(pic_path+'\n')
                # 以每张图为对应创建.txt标注train文件
                lable_txt_file_train = open(DATASET_PATH+'/pytorch_labels/'
                                            +(Path(line[0]+'txt').name),'w')
            image = Image.open(pic_path)
            
            width, height = image.size
            print('Porccessing picture: {} | width: {} Height: {}'.format(pic_path, width, height))

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

                if is_val:
                    lable_txt_file_val.write('{} {} {} {} {}\n'.format(box_class,x_center,y_center,box_w,box_h))
                else:
                    lable_txt_file_train.write('{} {} {} {} {}\n'.format(box_class,x_center,y_center,box_w,box_h))

            if is_val:
                lable_txt_file_val.close()
            else:
                lable_txt_file_train.close()

    train_list.close()
    train_list.close()
    

    return np.array(dataset)


# 主程序
if __name__ == '__main__':
    
    # 加载标注box的文件
    # data = load_dataset_voc(ANNO_PATH)
    anno_data = load_anno_txt(TRAIN_LIST_NAME)
    
