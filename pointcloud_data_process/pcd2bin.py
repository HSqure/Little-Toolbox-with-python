import os
import numpy as np
import fire
import torch
from pathlib import Path

SFX = 'pcd'
PCD_PATH='data/vox.pcd'

def get_file_name(input_file_path):
    return Path(input_file_path).stem

def get_file_path(input_file_path):
    return str(Path(input_file_path).parent)

def pcd_file_loader(pcd_file_path):

    lidar = []
    if not SFX in pcd_file_path.suffix:
        raise Exception(f'input file must be [.pcd] file, but input file is [{csv_file_path.suffix}] file!')
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


def main(pcd_file_path=PCD_PATH):

    output_prefix = (get_file_path(pcd_file_path)
            + '/' + get_file_name(pcd_file_path)
            + '.bin')

    pcd_data = pcd_file_loader(pcd_file_path=Path(pcd_file_path))
    pcd_data.numpy().tofile(output_prefix)
    print('\n--- Convertion Complete ---\n')
    print(f'File Location: {output_prefix}\n')
    
if __name__ == "__main__":
    fire.Fire()    