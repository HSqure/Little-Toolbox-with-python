
import os
import numpy as np
import fire
import torch
from pathlib import Path

SFX = 'pcd'
PCD_PATH='../source/lidar/'
PCD_OUTPUT_PATH='../velodyne/'

COORI_LIST_FILE_PATH='../source/label/lidar/'
OUTPUT_LIST_FILE_PATH='../label_2/'

'''
    File operation tools
'''
def file_name_scanner(file_dir):        
    file_name_list = os.listdir(file_dir)
    return file_name_list

def get_file_name(input_file_path):
    return Path(input_file_path).stem

def get_file_path(input_file_path):
    return str(Path(input_file_path).parent)

'''
    Point cloud data loader
'''
def pcd_file_loader(pcd_file_path):

    lidar = []
    if not SFX in pcd_file_path.suffix:
        raise Exception(f'input file must be [.pcd] file, but input file is [{pcd_file_path.suffix}] file!')
    else:
        with open(pcd_file_path,'r') as f:
            line = f.readline().strip()
            while line:
                linestr = line.split(" ")
                if len(linestr) == 4:
                    linestr_convert = list(map(float, linestr))
                    lidar.append(linestr_convert)
                line = f.readline().strip()   

        pcd_data = torch.from_numpy(np.array(lidar).reshape(-1, 4).astype(np.float32))
    
    return pcd_data

'''
    Coordinate Converse: velodyne -> cammera
'''
def coordi_velo2cam(velodyne_axis):
    camera_axis = torch.tensor([(-velodyne_axis[1]),        # velodyne Y -> camera X 
                                (-velodyne_axis[2] - 0.08),  # velodyne Z -> camera Y
                                (velodyne_axis[0] + 0.27)], # velodyne X -> camera Z
                                dtype=torch.float32)
    return camera_axis

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
        output = ((num1[0] - num2[0])**2 + (num1[2] - num2[2])**2 )**(1/2)
    elif dim==3:
        output = ((num1[0] - num2[0])**2 + (num1[2] - num2[2])**2 + (num1[1] - num2[1])**2 )**(1/2)
    else:
        raise Exception(f'Dimention could be 2 or 3 but not {dim} !')

    return output


'''
    get label
'''
def label_list(file_name):
    output_list_file = open(OUTPUT_LIST_FILE_PATH + file_name, 'w')
    annotation_set = open(COORI_LIST_FILE_PATH + file_name).read().split('\n')
    # annotation_set_image = open(COORI_LIST_FILE_PATH_IMAGE).read().split('\n')
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
        top_upperleft = coordi_velo2cam(torch.tensor([float(line[4]),
                                                        float(line[5]),
                                                        float(line[6])], dtype=torch.float32))

        top_upperright = coordi_velo2cam(torch.tensor([float(line[7]),
                                                        float(line[8]),
                                                        float(line[9])], dtype=torch.float32))

        top_lowerright = coordi_velo2cam(torch.tensor([float(line[10]),
                                                        float(line[11]),
                                                        float(line[12])], dtype=torch.float32))

        top_lowerleft = coordi_velo2cam(torch.tensor([float(line[13]),
                                                        float(line[14]),
                                                        float(line[15])], dtype=torch.float32))
        
        # box底层四个坐标
        bottom_upperleft = coordi_velo2cam(torch.tensor([float(line[16]),
                                                        float(line[17]),
                                                        float(line[18])], dtype=torch.float32))

        bottom_upperright = coordi_velo2cam(torch.tensor([float(line[19]),
                                                        float(line[20]),
                                                        float(line[21])], dtype=torch.float32))

        bottom_lowerright = coordi_velo2cam(torch.tensor([float(line[22]),
                                                        float(line[23]),
                                                        float(line[24])], dtype=torch.float32))

        bottom_lowerleft = coordi_velo2cam(torch.tensor([float(line[25]),
                                                        float(line[26]),
                                                        float(line[27])], dtype=torch.float32))



        rotation_y = (torch.acos((top_lowerright[0] - bottom_upperright[0])
                                        / L2norm(top_lowerright, bottom_upperright)) 
                                        * (-(top_lowerright[2] - bottom_upperright[2]) # 符号判断
                                        / torch.abs(top_lowerright[2] - bottom_upperright[2])))

        obj_center_axis = torch.tensor([(bottom_upperleft[0] + bottom_lowerright[0])/2, 
                                        (bottom_upperleft[1] + bottom_lowerright[1])/2,
                                        (bottom_upperleft[2] + bottom_lowerright[2])/2], dtype=torch.float32)

        # 方位角
        delta = (torch.acos((obj_center_axis[2]) / L2norm(obj_center_axis)) 
                * (-obj_center_axis[0]/torch.abs(obj_center_axis[0]))) # 符号判断
        alpha = rotation_y - delta
        # 长宽高
        tmp1 = L2norm(bottom_lowerright, bottom_upperright, dim=3)
        tmp2 = L2norm(bottom_lowerleft, bottom_lowerright, dim=3)
        length = tmp1 if tmp1>tmp2 else tmp2
        width = tmp1 if tmp1<tmp2 else tmp2
        height = L2norm(top_lowerright, bottom_lowerright, dim=3)

        # 输出
        output_list_file.write(f'{category} 0.00 0 {alpha} 1 1 2 2 {height} {length} {width} {obj_center_axis[0]} {obj_center_axis[1]} {obj_center_axis[2]} {rotation_y}')
        output_list_file.write('\n')

    output_list_file.close()



'''
    velodyne
'''
def velodyne_list(pcd_file_path):
    output_prefix = (PCD_OUTPUT_PATH
                    + get_file_name(pcd_file_path)
                    + '.bin')
    pcd_data = pcd_file_loader(pcd_file_path=Path(pcd_file_path))
    pcd_data.numpy().tofile(output_prefix)



def main():
    # ------ [1]. 标签文件转换 ------ 
    lable_file_name_list = file_name_scanner(COORI_LIST_FILE_PATH)
    for lable_file_name in lable_file_name_list:
        print(f'Processing {lable_file_name}')
        label_list(lable_file_name)
    print('\n--- Lable File Convertion Complete ---\n')
    # print(f'File Location: {output_prefix}\n')

    # ------ [2]. 点云文件转换 ------ 
    velodyne_file_name_list = file_name_scanner(PCD_PATH)
    for velodyne_file_name in velodyne_file_name_list:
        print(f'Processing {velodyne_file_name}')
        velodyne_list(PCD_PATH + velodyne_file_name)    

    print('\n--- Point Cloud Convertion Complete ---\n')
    # print(f'File Location: {output_prefix}\n')

if __name__ == "__main__":
    fire.Fire()
