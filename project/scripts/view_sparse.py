import os
import pycolmap
import open3d as o3d
import numpy as np

# --------------------------------------
# CONFIG
# --------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_DIR = os.path.join(PROJECT_DIR, "colmap_workspace")

SPARSE_MODEL_DIR = os.path.join(WORKSPACE_DIR, "sparse", "0")


# --------------------------------------
# LOAD SPARSE MODEL
# --------------------------------------
def load_sparse_model(model_path):
    print("📡 Loading COLMAP sparse model:", model_path)
    model = pycolmap.Reconstruction(model_path)
    print(f"✔ Loaded: {len(model.points3D)} points, "
          f"{len(model.images)} registered images")
    return model


# --------------------------------------
# BUILD OPEN3D POINT CLOUD
# --------------------------------------
def make_point_cloud(model):
    print("🟢 Converting COLMAP points → Open3D")

    pts = []
    colors = []

    for p in model.points3D.values():
        pts.append(p.xyz)

        if p.color is not None:
            colors.append(np.array(p.color) / 255.0)
        else:
            colors.append(np.array([0.7, 0.7, 0.7]))

    pts = np.array(pts)
    colors = np.array(colors)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    print(f"✔ Point cloud ready: {len(pts)} points")
    return pcd


# --------------------------------------
# CAMERA FRUSTUMS (OPTIONAL)
# --------------------------------------
def make_camera_frustums(model, scale=0.2):
    frustums = []

    for img in model.images.values():

        # Convert Rigid3d → 4×4 numpy matrix
        T_cw = img.cam_from_world().matrix()   # ✔ FIXED
        R_cw = T_cw[:3, :3]
        C = img.projection_center              # (3,) camera center

        # colmap stores R_cw (world → camera)
        R_wc = R_cw.T                           # invert rotation

        # Camera axes in world coordinates
        forward = R_wc @ np.array([0, 0, 1])
        right   = R_wc @ np.array([1, 0, 0])
        up      = R_wc @ np.array([0, -1, 0])

        f = forward * scale
        r = right   * (scale * 0.5)
        u = up      * (scale * 0.5)

        p0 = C
        p1 = C + f + r + u
        p2 = C + f - r + u
        p3 = C + f - r - u
        p4 = C + f + r - u

        points = np.vstack([p0, p1, p2, p3, p4]).astype(np.float64)
        lines = [
            [0,1],[0,2],[0,3],[0,4],
            [1,2],[2,3],[3,4],[4,1]
        ]

        ls = o3d.geometry.LineSet()
        ls.points = o3d.utility.Vector3dVector(points)
        ls.lines  = o3d.utility.Vector2iVector(lines)

        frustums.append(ls)

    return frustums




# --------------------------------------
# MAIN VIEWER
# --------------------------------------
def main():
    if not os.path.exists(SPARSE_MODEL_DIR):
        print("❌ Sparse model not found:", SPARSE_MODEL_DIR)
        return

    model = load_sparse_model(SPARSE_MODEL_DIR)
    pcd = make_point_cloud(model)
    frustums = make_camera_frustums(model)

    print("👀 Launching viewer...")
    o3d.visualization.draw_geometries([pcd, *frustums])


if __name__ == "__main__":
    main()
