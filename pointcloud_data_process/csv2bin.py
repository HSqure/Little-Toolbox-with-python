import mayavi.mlab
import torch
import fire
import numpy as np
import csv

CSV_PATH='data/car.csv'
BIN_SAVE_PATH='data/car.bin'

def csv_file_loader(csv_file_path):
    with open(csv_file_path,'r') as f:
        reader = csv.reader(f)
        # print(type(reader))
        csv_data=torch.tensor([[float(row[8]),
                                float(row[9]),
                                float(row[10]),
                                float(row[11])] for idx, row in enumerate(reader) if not idx==0])

    return csv_data


def main(csv_file_path=CSV_PATH, bin_save_path=BIN_SAVE_PATH):
    csv_data=csv_file_loader(csv_file_path=csv_file_path)
    csv_data.numpy().tofile(BIN_SAVE_PATH)

if __name__=="__main__":
    fire.Fire()