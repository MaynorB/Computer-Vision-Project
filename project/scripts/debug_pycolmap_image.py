import pycolmap
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE = os.path.join(PROJECT_DIR, "colmap_workspace")
SPARSE = os.path.join(WORKSPACE, "sparse", "0")

print("SPARSE_PATH =", SPARSE)

model = pycolmap.Reconstruction(SPARSE)

img = next(iter(model.images.values()))

print("\n🧪 Image attributes:")
print(dir(img))

print("\n🔍 Dump object:")
print(img)
