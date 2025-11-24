import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Import COLMAP's binary model parser
from read_write_model import read_points3d


SPARSE_MODEL_DIR = "project/colmap_workspace/sparse/0"


def visualize_sparse_matplotlib():
    points_path = os.path.join(SPARSE_MODEL_DIR, "points3D.bin")

    if not os.path.exists(points_path):
        print("❌ points3D.bin not found. Did COLMAP finish running?")
        return

    print("📥 Loading COLMAP 3D points…")
    pts3D = read_points3d(points_path)

    xyz = np.array([p.xyz for p in pts3D.values()])

    if xyz.size == 0:
        print("❌ No 3D points found in the reconstruction.")
        return

    print(f"📌 Loaded {xyz.shape[0]} 3D points.")

    # Plot
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(
        xyz[:, 0], xyz[:, 1], xyz[:, 2],
        s=2, depthshade=True
    )

    ax.set_title("COLMAP Sparse 3D Reconstruction (Matplotlib)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_sparse_matplotlib()
