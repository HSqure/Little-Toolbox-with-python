
import os
import numpy as np
import fire
import torch

import cmath


LIST_FILE_PATH='../label_2/0000.txt'
OUTPUT_LIST_FILE='output.txt'

'''
    File scan tools
'''
def file_name_scanner(file_dir):        
    file_name_list = os.listdir(file_dir)
    for item in file_name_list:
        print(item)
    return file_name_list

# '''
#     calib
# '''
# def camara_calib_list():


# '''
#     image
# '''
# def image_list():

def L2norm(num1, num2=None, dim=2):
    if num2 is None:
        num2 = torch.tensor([0,0,0],dtype=torch.float32)
    if dim==2:
        output = ((num1[0] - num2[0])**2 + (num1[1] - num2[1])**2 )**(1/2)
    elif dim==3:
        output = ((num1[0] - num2[0])**2 + (num1[1] - num2[1])**2 + (num1[2] - num2[2])**2 )**(1/2)
    else:
        raise Exception(f'Dimention could be 2 or 3 but not {dim} !')

    return output


'''
    label
'''
def label_list():
    output_list_file = open(OUTPUT_LIST_FILE, 'w')
    annotation_set = open(LIST_FILE_PATH).read().split('\n')

    for cnt, annotation_line in enumerate(annotation_set):
        # 判断非空        
        if not annotation_line: 
            continue
        line = annotation_line.strip('\n').split(' ')
        # line_image = annotation_set_image[cnt].strip('\n').split(' ')

        # 目标类型
        category = line[1]

        # 可见区域
        area = line[2].split('—')

        # box顶层四个坐标
        top_upperleft = torch.tensor([float(line[4]),
                                      float(line[5]),
                                      float(line[6])], dtype=torch.float32)

        top_upperright = torch.tensor([float(line[7]),
                                      float(line[8]),
                                      float(line[9])], dtype=torch.float32)

        top_lowerright = torch.tensor([float(line[10]),
                                      float(line[11]),
                                      float(line[12])], dtype=torch.float32)

        top_lowerleft = torch.tensor([float(line[13]),
                                      float(line[14]),
                                      float(line[15])], dtype=torch.float32)
        
        # box底层四个坐标
        bottom_upperleft = torch.tensor([float(line[16]),
                                      float(line[17]),
                                      float(line[18])], dtype=torch.float32)

        bottom_upperright = torch.tensor([float(line[19]),
                                      float(line[20]),
                                      float(line[21])], dtype=torch.float32)

        bottom_lowerright = torch.tensor([float(line[22]),
                                      float(line[23]),
                                      float(line[24])], dtype=torch.float32)

        bottom_lowerleft = torch.tensor([float(line[25]),
                                      float(line[26]),
                                      float(line[27])], dtype=torch.float32)



        rotation_y = torch.acos((torch.abs(top_lowerright[0] - bottom_upperright[0])
                                        / L2norm(top_lowerright, bottom_upperright)))                                        

        obj_center_axis = torch.tensor([(top_upperleft[0] + bottom_lowerright[0])//2, 
                                        (top_upperleft[1] + bottom_lowerright[1])//2,
                                        (top_upperleft[2] + bottom_lowerright[2])//2], dtype=torch.float32)

        # 方位角
        delta = torch.acos((torch.abs(obj_center_axis[1]) / L2norm(obj_center_axis)))              
        alpha = rotation_y - delta
        # 长宽高
        tmp1 = L2norm(bottom_lowerright, bottom_upperright, dim=3)
        tmp2 = L2norm(top_lowerleft, bottom_lowerright, dim=3)
        length = tmp1 if tmp1>tmp2 else tmp2
        width = tmp1 if tmp1<tmp2 else tmp2
        height = L2norm(top_lowerright, bottom_lowerright, dim=3)

        # 输出
        output_list_file.write(f'{category} 0.00 0 {alpha} 1 1 2 2 {height} {width} {length} {obj_center_axis[0]} {obj_center_axis[1]} {obj_center_axis[2]} {rotation_y}')
        output_list_file.write('\n')

    output_list_file.close()



# '''
#     velodyne
# '''
# def velodyne_list():



def main():
    label_list()


if __name__ == "__main__":
    fire.Fire()
