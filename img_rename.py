# coding=utf-8
"""
    本程序用于将目录下所有图片的图片名改为另一个目录下所有文件的文件名(按顺序)
"""
import os
import fire
from pathlib import Path

ROOT_DIR = '../../source/data/'
IMG_DIR = '/image/1/' #图片路径
NAME_DIR = '/lidar/1/' #标注文件路径

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
'''
    查找目录下所有文件名(默认按顺序输出)
'''
def file_name_scanner(file_dir, in_order=True):        
    file_name_list = os.listdir(file_dir)
    if in_order:
        # 排序
        file_name_list.sort()
    return file_name_list

def img_rename(dir_name):
    file_list = file_name_scanner(ROOT_DIR+dir_name+IMG_DIR) #查找标注文件目录下的所有文件名并保存在file_list里
    name_list = file_name_scanner(ROOT_DIR+dir_name+NAME_DIR)
    for cnt, item in enumerate(file_list):
        print( f'Renaming {item} -> {get_file_name(name_list[cnt])+get_file_suffix(item)}')
        Path(ROOT_DIR+dir_name+IMG_DIR+item).rename(Path(ROOT_DIR+dir_name+IMG_DIR+get_file_name(name_list[cnt])+get_file_suffix(item)))
    return cnt
          
def main():
    file_num=0
    root_dir_list=file_name_scanner(ROOT_DIR)
    for item in root_dir_list:
        num = img_rename(item)
        file_num=file_num+num
    print(f'\n ======= {file_num} Files Rename Complete ! ====== \n') 

if __name__ == '__main__':
    fire.Fire()
