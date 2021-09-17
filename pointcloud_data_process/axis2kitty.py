import os,shutil
import numpy as np
import fire
import torch
from pathlib import Path

# 源数据文件
ROOT_DIR = '../../source/'
# 转换后的存放路径
IMG_NEW='../../training/image_2/'
LABEL_NEW='../../training/label_2/'
VELODYNE_NEW='../../training/velodyne/'
# 点云文件后缀
SFX = 'pcd'

'''
    查找目录下所有文件名(默认按顺序输出)
'''
def file_name_scanner(file_dir, in_order=True):        
    file_name_list = os.listdir(file_dir)
    if in_order:
        # 排序
        file_name_list.sort()
    return file_name_list

'''
    获取文件名(去除后缀)
'''
def get_file_name(input_file_path):
    return Path(input_file_path).stem
'''
    获取文件后缀
'''
def get_file_suffix(input_file_path):
    return Path(input_file_path).suffix

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

"""
    数据集转换工具箱类
    AXIS -> KITTI
"""
class DatasetTransTools:

    def __init__(self):
        # 计数器
        self.__label_cnt=0
        self.__velodyne_cnt=0
        self.__img_cnt=0
        self.obj_class_name=[]

    '''
        坐标转换
        Coordinate Converse: velodyne -> cammera
    '''
    def coordi_velo2cam(self, velodyne_axis):
        camera_axis = torch.tensor([(-velodyne_axis[1]),        # velodyne Y -> camera X 
                                    (-velodyne_axis[2] - 0.08),  # velodyne Z -> camera Y
                                    (velodyne_axis[0] - 0.27)], # velodyne X -> camera Z
                                    dtype=torch.float32)
        return camera_axis

    '''
        L2范数
    '''
    def L2norm(self, num1, num2=None, dim=2):
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
        rotation_y计算
    '''
    def rotation_y_calcu(self, axis_1, axis_2):
        rotation_y = (torch.acos((axis_1[0] - axis_2[0])
                                / self.L2norm(axis_1, axis_2)))
        # 向量中的z>0时rotation_y<0
        if (axis_1[2] - axis_2[2])>=0:
            return torch.neg(rotation_y)
        else:
            return torch.abs(rotation_y)

    '''
        get class and count number
        统计类别名称以及频度并以字典形式保存
    '''
    def class_name_analyzer(self, object_name_list):
        category_lib={}
        for obj_name in object_name_list:
            # 将未出现过的类别加入字典，出现过的则统计+1
            category_lib[obj_name]=0 if (obj_name not in category_lib) else (category_lib[obj_name]+1)
        print(category_lib)

    '''
        get label
    '''
    def label_list(self, file_name, file_idx, output_path):
        output_list_file = open(output_path + '{:06d}'.format(file_idx) + '.txt', 'w')
        annotation_set = open(file_name).read().split('\n')

        for cnt, annotation_line in enumerate(annotation_set):
            # 判断非空        
            if not annotation_line: 
                continue
            line = annotation_line.strip('\n').split(' ')

            # 目标类型
            category = line[1]
            self.obj_class_name.append(line[1])

            # 可见区域
            area = line[2].split('—')

            # box顶层四个坐标
            top_upperleft = self.coordi_velo2cam(torch.tensor([float(line[4]),
                                                            float(line[5]),
                                                            float(line[6])], dtype=torch.float32))

            top_upperright = self.coordi_velo2cam(torch.tensor([float(line[7]),
                                                            float(line[8]),
                                                            float(line[9])], dtype=torch.float32))

            top_lowerright = self.coordi_velo2cam(torch.tensor([float(line[10]),
                                                            float(line[11]),
                                                            float(line[12])], dtype=torch.float32))

            top_lowerleft = self.coordi_velo2cam(torch.tensor([float(line[13]),
                                                            float(line[14]),
                                                            float(line[15])], dtype=torch.float32))
            
            # box底层四个坐标
            bottom_upperleft = self.coordi_velo2cam(torch.tensor([float(line[16]),
                                                            float(line[17]),
                                                            float(line[18])], dtype=torch.float32))

            bottom_upperright = self.coordi_velo2cam(torch.tensor([float(line[19]),
                                                            float(line[20]),
                                                            float(line[21])], dtype=torch.float32))

            bottom_lowerright = self.coordi_velo2cam(torch.tensor([float(line[22]),
                                                            float(line[23]),
                                                            float(line[24])], dtype=torch.float32))

            bottom_lowerleft = self.coordi_velo2cam(torch.tensor([float(line[25]),
                                                            float(line[26]),
                                                            float(line[27])], dtype=torch.float32))

            rotation_y = self.rotation_y_calcu(top_lowerright, bottom_upperright)

            obj_center_axis = torch.tensor([(bottom_upperleft[0] + bottom_lowerright[0])/2, 
                                            (bottom_upperleft[1] + bottom_lowerright[1])/2,
                                            (bottom_upperleft[2] + bottom_lowerright[2])/2], dtype=torch.float32)

            # 方位角
            delta = (torch.acos((obj_center_axis[2]) / self.L2norm(obj_center_axis)) 
                    * (-obj_center_axis[0]/torch.abs(obj_center_axis[0]))) # 符号判断
            alpha = rotation_y - delta
            # 长宽高
            tmp1 = self.L2norm(bottom_lowerright, bottom_upperright, dim=3)
            tmp2 = self.L2norm(bottom_lowerleft, bottom_lowerright, dim=3)
            length = tmp1 if tmp1>tmp2 else tmp2
            width = tmp1 if tmp1<tmp2 else tmp2
            height = self.L2norm(top_lowerright, bottom_lowerright, dim=3)

            # 输出
            output_list_file.write(f'{category} 0.00 0 {alpha} 1 1 2 2 {height} {length} {width} {obj_center_axis[0]} {obj_center_axis[1]} {obj_center_axis[2]} {rotation_y}')
            output_list_file.write('\n')

        output_list_file.close()

    '''
        velodyne
    '''
    def pcd2bin(self, pcd_file_path, file_idx, output_path):
        output_prefix = (output_path
                        + '{:06d}'.format(file_idx)
                        + '.bin')
        pcd_data = pcd_file_loader(pcd_file_path=Path(pcd_file_path))
        pcd_data.numpy().tofile(output_prefix)

    '''
        转换过程总控
    '''
    def trans(self, set_name):

        label_path = ROOT_DIR+'label/'+set_name+'/lidar/1/'
        pcd_path = ROOT_DIR+'data/'+set_name+'/lidar/1/'
        img_path = ROOT_DIR+'data/'+set_name+'/image/1/'

        # ------ [1]. 标签文件转换 ------ 
        lable_file_name_list = file_name_scanner(label_path)
        for idx, lable_file_name in enumerate(lable_file_name_list):
            print(f'Processing {lable_file_name}')
            self.label_list(label_path + lable_file_name, self.__label_cnt+idx, LABEL_NEW)
        self.__label_cnt = self.__label_cnt + idx + 1
        print(f'\n--- Label set {set_name} Convertion Complete ---\n')
        # print(f'File Location: {output_prefix}\n')

        # ------ [2]. 点云文件转换 ------ 
        velodyne_file_name_list = file_name_scanner(pcd_path)
        for idx, velodyne_file_name in enumerate(velodyne_file_name_list):
            print(f'Processing {velodyne_file_name}')
            self.pcd2bin(pcd_path + velodyne_file_name, self.__velodyne_cnt + idx, VELODYNE_NEW)
        self.__velodyne_cnt = self.__velodyne_cnt + idx + 1
        print(f'\n--- Point Cloud Set {set_name} Convertion Complete ---\n')
        # print(f'File Location: {output_prefix}\n')

        # ------ [3]. 图像文件复制 ------
        img_name_list = file_name_scanner(img_path)
        for idx, img_name in enumerate(img_name_list):
            shutil.copy(img_path+img_name, IMG_NEW)
            shutil.move(IMG_NEW+img_name, IMG_NEW + '{:06d}'.format(self.__img_cnt + idx) + get_file_suffix(img_name)) # 重命名为新的绝对路径
        self.__img_cnt = self.__img_cnt + idx + 1
        print(f'\n--- Image Set {set_name} Convertion Complete ---\n')

    '''
        获取子文件夹目录名，进入后开始转换并分析标签文件
    '''
    def trans_running(self):
        set_name_list = file_name_scanner(ROOT_DIR+'data')
        for item in set_name_list:
            self.trans(item)
        #统计并分析所有类别
        self.class_name_analyzer(self.obj_class_name)
        # print(f'\n ======= {file_num} Files Move Complete ! ====== \n')         


def main():
    datasettranstools = DatasetTransTools()
    datasettranstools.trans_running()

if __name__ == "__main__":
    fire.Fire()
