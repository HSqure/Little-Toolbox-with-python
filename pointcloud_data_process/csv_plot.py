import mayavi.mlab
import torch
import fire
import numpy as np
import csv

CSV_PATH='data/car.csv'

def csv_file_loader(csv_file_path):
    with open(csv_file_path,'r') as f:
        reader = csv.reader(f)
        # print(type(reader))
        csv_data=torch.tensor([[float(row[8]),
                                float(row[9]),
                                float(row[10]),
                                float(row[11])] for idx, row in enumerate(reader) if not idx==0])

    return csv_data

def viz_mayavi(points,vals="reflectivity"):
    x=points[:,0]
    y=points[:,1]
    z=points[:,2]
    r=points[:,3]
    d=torch.sqrt(x**2+y**2)

    if vals=="height":
        col=z
    elif vals=="reflectivity":
        col=r
    else:
        col=d

    fig=mayavi.mlab.figure(bgcolor=(0,0,0),size=(1280,720))
    mayavi.mlab.points3d(x,y,z,
                         col,
                         mode="point",
                         colormap='spectral',
                         figure=fig,)

    mayavi.mlab.show()

def main(csv_file_path=CSV_PATH):
    csv_data=csv_file_loader(csv_file_path=csv_file_path)
    viz_mayavi(csv_data,vals="d")

if __name__=="__main__":
    fire.Fire()