import mayavi.mlab
import torch
import fire
import numpy as np

BIN_PATH='data/000002.bin'

def bin_file_load(bin_file_path):
    pointclouddata=np.fromfile(bin_file_path,dtype=np.float32,count=-1).reshape([-1,4])
    pointclouddata=torch.from_numpy(pointclouddata)
    print(f'\nPoint Cloud Size: {pointclouddata.size()}')
    print(f'Point Cloud Type: {pointclouddata.type()}\n')

    return pointclouddata

def viz_mayavi(points,vals="distance"):
    x=points[:,0]
    y=points[:,1]
    z=points[:,2]
    r=points[:,3]
    d=torch.sqrt(x**2+y**2)

    if vals=="height":
        col=z
    else:
        col=d

    fig=mayavi.mlab.figure(bgcolor=(0,0,0),size=(1280,720))
    mayavi.mlab.points3d(x,y,z,
                         col,
                         mode="point",
                         colormap='spectral',
                         figure=fig,)

    mayavi.mlab.show()

def main(bin_file_path=BIN_PATH):
    pointclouddata = bin_file_load(bin_file_path=bin_file_path)
    viz_mayavi(pointclouddata,vals="height")

if __name__=="__main__":
    fire.Fire()

