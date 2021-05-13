# coding=utf-8
"""
将voc数据集信息导入自己的annotation文件

"""

import xml.etree.ElementTree as ET
from os import getcwd

# 数据集图片类型
PIC_FORMAT = 'jpg' 

# voc数据集路径
DATASET_PATH = '/home/huahua/Workspace/dataset/APPLE2021/train/'
XML_FILE = DATASET_PATH + 'Annotations/'
IMAGE_IDS_PATH = DATASET_PATH + 'ImageSets/Main/'
IMG_PATH = DATASET_PATH + 'JPEGImages/'

DATA_LIST_FILE_NAME = 'train.txt'
TRAIN_LIST_NAME = 'apple_train.txt'

# # 目标种类字典
# CATEGORY_DICT = {'apple':0, 
#                  'damaged_apple':1}

#如需修改，将此改成自己的classes
CATEGORY = ['apple','damaged_apple']

# 单xml文件含单图像的标注信息
def read_anno_from_voc_xml(image_id, list_file):
    classes = CATEGORY
    xml_file = open(XML_FILE+'{}.xml'.format(image_id))
    tree = ET.parse(xml_file)
    root = tree.getroot()

    list_file.write(IMG_PATH + str(image_id) + '.' + PIC_FORMAT) # 写入图片地址

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text), int(xmlbox.find('xmax').text), int(xmlbox.find('ymax').text))
        list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))

    list_file.write('\n')


# 单xml文件含多个图像(图片组)的标注信息,id为图片组的id
def read_anno_from_group_xml(file_id, list_file):
    xml_file = open(XML_FILE+'{}.xml'.format(group_id))
    tree = ET.parse(xml_file)
    root = tree.getroot()
    category = CATEGORY_DICT

    # 在每一组中遍历所有图片(frame)
    for frame in root.iter('frame'):
        # 获取图片id
        img_id = frame.get('num')
        # 打印所在训练集图片组地址
        list_file.write(IMG_PATH + str(group_id) + '/' + 'img{:0>5d}.jpg'.format(int(img_id))) # 填充左边,宽度为5

        # 进入子节点(target的集合list)
        target_list = frame.find('target_list')
        # 在每一张图(frame)的target_list中遍历所有target的box
        for target in target_list.findall('target'):

            # 获取车辆类别信息
            vehicle_type = target.find('attribute').get('vehicle_type')

            # 获取目标框gt信息
            box = target.find('box')
            height = float(box.get('height'))
            left = float(box.get('left'))
            top = float(box.get('top'))
            width = float(box.get('width'))

            # 打印box的gt框值,并进行(height,left,top,width)到(xmin,ymin,xmax,ymax)的转换
            list_file.write(' {},{},{},{},{}'.format(int(left), int(top), int(left+width), int(top+height), category[vehicle_type]))

            # print('Group id: {} | Img id: {} | Box info: {},{},{},{}'.format(group_id, img_id, height, left, top, width))

        list_file.write('\n')


if __name__ == '__main__':

    image_ids = open(IMAGE_IDS_PATH + DATA_LIST_FILE_NAME).read().split('\n') # 导入对应的图片名list文件，取图片id，以换行为标志分割
    list_file = open(TRAIN_LIST_NAME, 'w') # 创建自己的annotation文件，数据由voc导入

    # 从训练用的image list 文本文件中取出图像id
    for image_id in image_ids:
        if image_id=='':
            break

        # 根据id从.xml文件中取得标注信息
        read_anno_from_voc_xml(image_id, list_file)

    list_file.close()