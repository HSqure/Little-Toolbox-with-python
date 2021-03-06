import mayavi.mlab
import torch
import fire
import numpy as np
import csv
from pathlib import Path

SFX = 'csv'
CSV_PATH='data/car.csv'

def get_file_name(input_file_path):
    return Path(input_file_path).stem

def get_file_path(input_file_path):
    return str(Path(input_file_path).parent)

def csv_file_loader(csv_file_path):

    if not SFX in csv_file_path.suffix:
        raise Exception(f'input file must be [.csv] file, but input file is [{csv_file_path.suffix}] file!')
    else:
        with open(csv_file_path,'r') as f:
            reader = csv.reader(f)
            # print(type(reader))
            csv_data=torch.tensor([[float(row[8]),
                                    float(row[9]),
                                    float(row[10]),
                                    float(row[11])] for idx, row in enumerate(reader) if not idx==0])

    return csv_data

def main(csv_file_path):

    output_prefix = (get_file_path(csv_file_path)
                            + '/' + get_file_name(csv_file_path)
                            + '.bin')

    csv_data=csv_file_loader(csv_file_path=Path(csv_file_path))
    csv_data.numpy().tofile(output_prefix)
    print('\n--- Convertion Complete ---\n')
    print(f'File Location: {output_prefix}\n')

if __name__=="__main__":
    fire.Fire()