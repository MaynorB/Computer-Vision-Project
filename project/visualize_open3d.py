import os
import numpy as np
import open3d as o3d

# Import COLMAP binary model reader
from read_write_model import read_points3d


SPARSE_MODEL_DIR = "project/colmap_workspace/sparse/0"


def visualize_sparse_open3d():
    points_path = os.path.join(SPARSE_MODEL_DIR, "points3D.bin")

    if not os.path.exists(points_path):
        print("❌ points3D.bin not found. Run COLMAP first.")
        return

    print("📥 Loading COLMAP 3D points…")
    pts3D = read_points3d(points_path)

    xyz = np.array([p.xyz for p in pts3D.values()])

    if xyz.size == 0:
        print("❌ No 3D points found.")
        return

    print(f"📌 Loaded {xyz.shape[0]} 3D points.")

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)

    print("🖥️ Launching Open3D viewer…")
    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    visualize_sparse_open3d()
