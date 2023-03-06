
import open3d as o3d
import numpy as np

# 读取二进制点云文件
point_cloud = np.fromfile('/home/alinx/Downloads/000000.bin', dtype=np.float32)
point_cloud = np.reshape(point_cloud, (-1, 4))

print(point_cloud[:, 3:])

# 创建点云对象
pcd = o3d.geometry.PointCloud()

# 设置点云的坐标和颜色
pcd.points = o3d.utility.Vector3dVector(point_cloud[:, :3])
print(pcd.has_colors())
# pcd.colors = o3d.utility.Vector3dVector(np.asarray(point_cloud[:, 3:] / 255.0))

# 显示点云
o3d.visualization.draw_geometries([pcd])
