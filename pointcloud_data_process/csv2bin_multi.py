"""
    以20000行为一帧将csv点云记录文件拆分成多个bin文件
"""

import torch
import fire
import numpy as np
import csv
from pathlib import Path

MS200=19999


SFX = 'csv'
CSV_PATH='../../../sample/street_test.csv'
SAVE_PATH='../../../sample/street_test/'

def get_file_name(input_file_path):
    return Path(input_file_path).stem

def get_file_path(input_file_path):
    return str(Path(input_file_path).parent)

class CSVConverter:

    def __init__(self):
            # 计数器
            self.__row_cnt=0
            self.__file_cnt=0

    def csv_file_loader(self, csv_file_path):
        if not SFX in csv_file_path.suffix:
            raise Exception(f'input file must be [.csv] file, but input file is [{csv_file_path.suffix}] file!')
        else:
            with open(csv_file_path,'r') as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    # avoid header row
                    if idx==0:
                       csv_data=[]
                       self.__file_cnt=0
                    elif not idx%MS200==0:
                        csv_data.append([float(row[8]),
                                        float(row[9]),
                                        float(row[10]),
                                        float(row[11])])                         
                    else:
                        print('Saving {:06d}.bin'.format(self.__file_cnt))
                        torch.tensor(csv_data).numpy().tofile(SAVE_PATH+'{:06d}.bin'.format(self.__file_cnt))
                        csv_data=[]
                        self.__file_cnt+=1         
        # return csv_data

    def convert(self, csv_file_path=CSV_PATH):
        self.csv_file_loader(csv_file_path=Path(csv_file_path))
        print('\n--- Convertion Complete ---\n')

def main():
    csv_convert = CSVConverter()
    csv_convert.convert()

if __name__=="__main__":
    fire.Fire()
