import os
import subprocess
from tqdm import tqdm
import cv2


# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
IMAGE_DIR = "project/images"
COLMAP_WORKSPACE = "project/colmap_workspace"
SPARSE_ROOT = os.path.join(COLMAP_WORKSPACE, "sparse")
DENSE_DIR = os.path.join(COLMAP_WORKSPACE, "dense")

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


# -------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------

def collect_images(image_dir):
    """
    Scan directory for valid images, show progress bar, and warn about invalid files.
    """
    print(f"\n📁 Scanning folder for images: {image_dir}\n")

    if not os.path.exists(image_dir):
        print("❌ ERROR: Image directory does not exist!")
        return []

    found_images = []
    all_files = os.listdir(image_dir)

    for filename in tqdm(all_files, desc="Scanning", unit="file"):
        filepath = os.path.join(image_dir, filename)
        ext = os.path.splitext(filename.lower())[1]

        # Skip directories
        if os.path.isdir(filepath):
            continue

        # Unsupported formats
        if ext not in VALID_EXTENSIONS:
            print(f"⚠️ WARNING: Skipping unsupported file: {filename}")
            continue

        # Try to read the image to check for corruption
        if cv2.imread(filepath) is None:
            print(f"❌ ERROR: Could not read (corrupt?) image: {filename}")
            continue

        found_images.append(filepath)

    print(f"\n✅ Found {len(found_images)} valid images.\n")
    return found_images



def detect_sparse_folder():
    """
    Find the generated sparse folder (0, 1, 2, ...)
    """
    if not os.path.exists(SPARSE_ROOT):
        return None

    subfolders = [
        os.path.join(SPARSE_ROOT, f)
        for f in os.listdir(SPARSE_ROOT)
        if os.path.isdir(os.path.join(SPARSE_ROOT, f))
    ]

    if not subfolders:
        return None

    # Pick the first (usually "0")
    return subfolders[0]



def run_colmap(images):
    """
    Run COLMAP feature extraction, matching, and sparse reconstruction.
    Only prints progress and output location.
    """
    if not images:
        print("❌ No valid images found. Exiting.")
        return

    print("\n🚀 Running COLMAP on your images...\n")

    # Ensure directories exist
    os.makedirs(COLMAP_WORKSPACE, exist_ok=True)
    os.makedirs(SPARSE_ROOT, exist_ok=True)
    os.makedirs(DENSE_DIR, exist_ok=True)

    db_path = os.path.join(COLMAP_WORKSPACE, "database.db")

    # ----------------------------------------------------------
    # 1) Feature extraction
    # ----------------------------------------------------------
    print("🔍 Extracting features...")
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", db_path,
        "--image_path", IMAGE_DIR
    ], check=True)

    # ----------------------------------------------------------
    # 2) Matching
    # ----------------------------------------------------------
    print("\n🔗 Matching features...")
    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", db_path
    ], check=True)

    # ----------------------------------------------------------
    # 3) Sparse reconstruction
    # ----------------------------------------------------------
    print("\n📡 Sparse reconstruction...")
    subprocess.run([
        "colmap", "mapper",
        "--database_path", db_path,
        "--image_path", IMAGE_DIR,
        "--output_path", SPARSE_ROOT
    ], check=True)

    print("\n📁 Checking for COLMAP sparse output...\n")
    sparse_folder = detect_sparse_folder()

    if sparse_folder is None:
        print("❌ ERROR: No sparse reconstruction folder found in:")
        print(f"   {SPARSE_ROOT}")
        print("   Something went wrong during COLMAP reconstruction.")
        return

    print(f"✅ Sparse reconstruction detected:")
    print(f"   {sparse_folder}\n")

    # Print expected file presence
    expected_files = ["cameras.bin", "images.bin", "points3D.bin"]
    for f in expected_files:
        fp = os.path.join(sparse_folder, f)
        if os.path.exists(fp):
            print(f"   ✔ {f}")
        else:
            print(f"   ❌ {f} (missing!)")

    print("\nℹ️ Dense reconstruction not run. You can run it later manually.")
    print("\n🎉 Finished! COLMAP processed your images.\n")



# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
if __name__ == "__main__":
    print("\n====== COLMAP IMAGE PIPELINE (TEST MODE) ======\n")

    # Step 1: Collect and validate images
    images = collect_images(IMAGE_DIR)

    # Step 2: Run COLMAP
    run_colmap(images)
