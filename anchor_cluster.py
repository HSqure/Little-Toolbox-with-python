#coding=utf-8

"""
    本程序用于读取标注数据中的所有box,得到聚类后的指定数量(CLUSTERS)的anchor框
    详细原理参考: 目标检测算法之YOLO系列算法的Anchor聚类代码实战 https://zhuanlan.zhihu.com/p/95291364
"""

import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
import json
import glob

ANNO_PATH = ''
PORJ_PATH = '/home/huahua/Workspace/Tensorflow/keras-yolo3-trash/'

# yolo训练所需的annotation文本文件名与路径
TRAIN_LIST_NAME = PORJ_PATH + 'trash_train.txt'

# 存放生成的anchors数据的文本文件名与路径
GEN_ANCHOR_FILE_NAME = PORJ_PATH + 'model_data/' + 'yolo_anchors_trash.txt'

CLUSTERS = 9 #聚类数量，anchor数量
INPUTDIM = 416 #输入网络大小

'''
    计算一个ground truth边界盒和k个先验框(Anchor)的交并比(IOU)值。
    参数box: 元组或者数据，代表ground truth的长宽。
    参数clusters: 形如(k,2)的numpy数组，其中k是聚类Anchor框的个数
    返回：ground truth和每个Anchor框的交并比。
'''
def iou(box, clusters):

    x = np.minimum(clusters[:, 0], box[0])
    y = np.minimum(clusters[:, 1], box[1])
    if np.count_nonzero(x == 0) > 0 or np.count_nonzero(y == 0) > 0:
        raise ValueError("Box has no area")
    intersection = x * y
    box_area = box[0] * box[1]
    cluster_area = clusters[:, 0] * clusters[:, 1]
    iou_ = intersection / (box_area + cluster_area - intersection)
    return iou_

'''
    计算一个ground truth和k个Anchor的交并比的均值。
'''
def avg_iou(boxes, clusters):
    return np.mean([np.max(iou(boxes[i], clusters)) for i in range(boxes.shape[0])])

'''
    利用IOU值进行K-means聚类
    参数boxes: 形状为(r, 2)的ground truth框，其中r是ground truth的个数 
    参数k: Anchor的个数
    参数dist: 距离函数
    返回值：形状为(k, 2)的k个Anchor框
'''
def kmeans(boxes, k, dist=np.median):
    # 即是上面提到的r
    rows = boxes.shape[0]
    # 距离数组，计算每个ground truth和k个Anchor的距离
    distances = np.empty((rows, k))
    # 上一次每个ground truth"距离"最近的Anchor索引
    last_clusters = np.zeros((rows,))
    # 设置随机数种子
    np.random.seed()

    # 初始化聚类中心，k个簇，从r个ground truth随机选k个
    clusters = boxes[np.random.choice(rows, k, replace=False)]
    # 开始聚类
    while True:
        # 计算每个ground truth和k个Anchor的距离，用1-IOU(box,anchor)来计算
        for row in range(rows):
            distances[row] = 1 - iou(boxes[row], clusters)
        # 对每个ground truth，选取距离最小的那个Anchor，并存下索引
        nearest_clusters = np.argmin(distances, axis=1)
        # 如果当前每个ground truth"距离"最近的Anchor索引和上一次一样，聚类结束
        if (last_clusters == nearest_clusters).all():
            break
        # 更新簇中心为簇里面所有的ground truth框的均值
        for cluster in range(k):
            clusters[cluster] = dist(boxes[nearest_clusters == cluster], axis=0)
        # 更新每个ground truth"距离"最近的Anchor索引
        last_clusters = nearest_clusters

    return clusters

'''
    加载VOC类数据集，需要所有labelimg标注出来的xml文件
'''
def load_dataset_voc(path):
    dataset = []
    for xml_file in glob.glob("{}/*xml".format(path)):
        tree = ET.parse(xml_file)
        # 图片高度
        height = int(tree.findtext("./size/height"))
        # 图片宽度
        width = int(tree.findtext("./size/width"))
        
        for obj in tree.iter("object"):
            # 偏移量
            xmin = np.float64(int(obj.findtext("bndbox/xmin")) / width)
            ymin = np.float64(int(obj.findtext("bndbox/ymin")) / height)
            xmax = np.float64(int(obj.findtext("bndbox/xmax")) / width)
            ymax = np.float64(int(obj.findtext("bndbox/ymax")) / height)

            if xmax == xmin or ymax == ymin:
                print(xml_file)
            # 将Anchor的长宽放入dateset，运行kmeans获得Anchor
            dataset.append([xmax - xmin, ymax - ymin])
    return np.array(dataset)

'''
    加载COCO类数据集，需要.json标注文件
'''
def load_dataset_coco(path): 
    # 打开.json标注文件
    f = open(path, encoding='utf-8')
    # 将文件所有信息保存在data中
    data = json.load(f)
    dataset = []
    # 从data中提取信息
    #category_index = data['categories'] # 全部类别索引
    image_info = data['images'] # 图片信息
    anno = data['annotations'] # 标注信息

    for info in image_info:
        pic_id = info['id'] # 取当前pic_id,在下面的循环中找到与其匹配的segmentation,即gt_box的坐标
        width = info['width']
        height = info['height']
        for gt in anno:
            # 查找同一图片下的所有gt_box (image_id为json对训练集图片的内部编号,与图片名无关)
            if gt['image_id'] == pic_id:
                # 取segmentation4组坐标中的xmin,ymin,xmax,ymax
                box_axis = (str(gt['segmentation'][0][0]) + ',' 
                          + str(gt['segmentation'][0][1]) + ',' 
                          + str(gt['segmentation'][0][4]) + ',' 
                          + str(gt['segmentation'][0][5]))
                # 偏移量
                xmin = np.float64(int(gt['segmentation'][0][0]) / width)
                ymin = np.float64(int(gt['segmentation'][0][1]) / height)
                xmax = np.float64(int(gt['segmentation'][0][4]) / width)
                ymax = np.float64(int(gt['segmentation'][0][5]) / height)

                if xmax == xmin or ymax == ymin:
                    print(gt['image_id'])
                # 将Anchor的长宽放入dateset，运行kmeans获得Anchor
                dataset.append([xmax - xmin, ymax - ymin])

                #print( 'proccessing {0:.2f}% completed'.format((pic_id/8861)*100))

    return np.array(dataset)

'''
    从生成的yolo训练所需的annotation文本文件中提取bbox
'''
def load_anno_txt(path):
    # 读取并存放全部annotation文本内容,以换行符为flag进行分行
    annotation_set = open(path).read().split('\n')
    dataset = []

    for annotation_line in annotation_set:
        if len(annotation_line)==0:
            continue
        # 剥离后缀,剥离后分为两段: 第1段为图片路径(缺个后缀), 第2段为该图片中的所有box的组
        line = annotation_line.strip('\n')
        pic_format = line.split('.')[1][0:3] # 查找后缀名
        line = line.split(pic_format)

        '''以下为对无标注box图像(用于样本均衡)的适应性判断 '''
        # 如果line有两个元素(图片地址与bbox),则说明有bbox
        # 否则该图片没有bbox标注
        if np.size(line)==2:
            image = Image.open(line[0]+pic_format) # 添加回后缀读取第1段的图片文件
            width, height = image.size
            print('Porccessing picture: {} | width: {} Height: {}'.format(line[0]+pic_format, width, height))

            # 将第2段的多个以空格分隔的box组分割后，把得到的每个box存放在list型的box_set_per_line中
            box_set_per_line = line[1].split(' ')

            # 开始解析每个box的坐标数据 
            for box in box_set_per_line:
                if len(box)==0:
                    continue
                # 每个box_axis包含box的4个信息(xmin,ymin,xmax,ymax)
                box_axis = box.split(',')
                # 偏移量
                xmin = np.float64(int(box_axis[0]) / width)
                ymin = np.float64(int(box_axis[1]) / height)
                xmax = np.float64(int(box_axis[2]) / width)
                ymax = np.float64(int(box_axis[3]) / height)
         
                if xmax == xmin or ymax == ymin:
                    print('Error box in Image File: {}'.format(str(line[0]+PIC_FORMAT)))
                # 将Anchor的长宽放入dateset，运行kmeans获得Anchor
                dataset.append([xmax - xmin, ymax - ymin])

    return np.array(dataset)

'''
    将生成的Anchor_box按yolo所需格式写入.txt文本文件
'''
def anchor_txt_write(anchor_data):
    anchor_file = open(GEN_ANCHOR_FILE_NAME, 'w') # 创建anchors数据文件
    # 使用枚举方式得到下标
    for sub_num,anchor_box in enumerate(anchor_data):
        if sub_num==CLUSTERS-1:
            anchor_file.write('{},{}'.format(int(anchor_box[0]),int(anchor_box[1])))
        else:
            anchor_file.write('{},{},  '.format(int(anchor_box[0]),int(anchor_box[1])))
    
    print('\nAnchors file has been generated at: {}\n'.format(GEN_ANCHOR_FILE_NAME))
    anchor_file.close()



# 主程序
if __name__ == '__main__':
    
    # 加载标注box的文件
    # data = load_dataset_voc(ANNO_PATH)
    data = load_anno_txt(TRAIN_LIST_NAME)
    # 进行kmeans聚类
    out = kmeans(data, k=CLUSTERS)
    # 后处理
    final_anchors_Boxes = np.array(out) * INPUTDIM

    # Anchor box 结果显示
    print('\nBoxes:\n{}\n'.format(final_anchors_Boxes)) 
    print('\nAccuracy: {:.2f}%'.format(avg_iou(data, out) * 100))
    # box比例结果显示
    final_anchors_scale = np.around(out[:, 0] / out[:, 1], decimals=2).tolist()
    print('\nBefore Sort Ratios:\n {}\n'.format(final_anchors_scale))
    print('\nAfter Sort Ratios:\n {}\n'.format(sorted(final_anchors_scale)))
    
    # 将anchor写入文本文件
    anchor_txt_write(final_anchors_Boxes)
