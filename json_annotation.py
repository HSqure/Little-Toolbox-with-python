# coding=utf-8

"""
    将coco数据集信息导入自己的annotation文件(.txt)

    数据集筛选: category(60种) -> supercategory(28种)(anno文件中将category中类别多对一映射标注以精简) -> 筛选后的数量排前11(数据集资料提供)的supercategory(11种)

"""

TRAIN_PATH = '/home/huahua/Workspace/dataset/TACO-trash-dataset/data/'
TRAIN_JSON_FILE_NAME = 'annotations.json'
PIC_PATH = TRAIN_PATH

LIST_FILE_PATH = './'
LIST_FILE_NAME = 'trash_train.txt'


import json
import numpy as np
from collections import defaultdict
from os import getcwd

# 特定类别组(数量前11)
CATE_WINDOW = [4,5,7,8,9,13,14,16,25,27,28]

'''
    用于修正类别id

    input: 
        catagory_id_old: 原catagory_id,
        id_dict: 新旧catagory_id对照字典

    output: 
        整合后的新的catagory_id
'''
def cat_fix(catagory_id_old, id_dict):
    
    return id_dict[str(catagory_id_old)]

'''
    Super Category类别整合,重新编号,输出查找表字典

    input: 
        categories: json中的categories列表
    output:
        id_dict: 新旧catagory_id对照字典
'''
def cat_id_dict_gen(categories):
    # 初始化
    cate_buff=''
    cate_id=0
    id_dict={}
    for category in categories:
        # 类别查重
        if not (cate_buff == category['supercategory']): # 如果类别名跟上次出现的不一样,才增发新的重新编码的id号
            # 新id编号
            cate_id = cate_id + 1
        cate_buff = category['supercategory']

        # 数据集筛选step1:创建旧id与重新编号的新id的对照字典,用于后面用新的替换旧的id
        # 数据集筛选step2:通过判断语句,仅仅将此类别组参与训练,其他类别都归到第'27类',随后根据列表下标从0-10重新编号
        if cate_id in CATE_WINDOW:
            id_dict[str(category['id'])] = str(CATE_WINDOW.index(cate_id))
        else:
            id_dict[str(category['id'])] = str(CATE_WINDOW.index(27))

    print(id_dict)
    return id_dict    

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
    categories = data['categories'] # 类别信息

    # 类别整合,重新编号,输出查找表字典
    id_dict = cat_id_dict_gen(categories)

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
                    str(int(gt['bbox'][0])) + ',' + 
                    str(int(gt['bbox'][1])) + ',' + 
                    str(int(gt['bbox'][0]+gt['bbox'][2])) + ',' + 
                    str(int(gt['bbox'][1]+gt['bbox'][3]))
                )
                box_category = gt['category_id']
                # 整合累加
                gt_box = str(gt_box) + ' ' + str(box_axis) + ',' + cat_fix(box_category, id_dict)
                # print( 'proccessing {0:.2f}% completed'.format((pic_id/1499)*100))

        # 将"图片路径"与"annotation信息"写入到.txt文件中
        list_file.write(pic_location + str(gt_box))
        list_file.write('\n')

    f.close()



if __name__ == '__main__':

    list_file = open(LIST_FILE_PATH+LIST_FILE_NAME, 'w')

    read_anno_from_coco_json(list_file)

    list_file.close()
