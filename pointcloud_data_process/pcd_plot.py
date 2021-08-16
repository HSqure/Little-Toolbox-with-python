import mayavi.mlab
import torch
import fire
import numpy as np

SFX = 'pcd'
PCD_PATH='data/vox.pcd'

def pcd_file_loader(pcd_file_path):

    lidar = []
    with open(pcd_file_path,'r') as f:
        line = f.readline().strip()
        while line:
            linestr = line.split(" ")
            if len(linestr) == 4:
                linestr_convert = list(map(float, linestr))
                lidar.append(linestr_convert)
            line = f.readline().strip()   

    pointclouddata = torch.from_numpy(np.array(lidar).reshape(-1, 4).astype(np.float32))
    print(f'\nPoint Cloud Size: {pointclouddata.size()}')
    print(f'Point Cloud Type: {pointclouddata.type()}\n')

    return pointclouddata

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

def main(bin_file_path=PCD_PATH):
    pointclouddata = pcd_file_loader(pcd_file_path=bin_file_path)
    viz_mayavi(pointclouddata,vals="reflectivity")

if __name__=="__main__":
    fire.Fire()

