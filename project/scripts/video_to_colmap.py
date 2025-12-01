#!/usr/bin/env python3
import os
import cv2
import glob
import shutil
import subprocess

# ============================================
#               CONFIGURATION
# ============================================

FRAME_RATE = 2              # FPS to sample from video
BLUR_THRESHOLD = 150        # strict blur filtering
MAX_FRAMES = 800            # safety cap

CAMERA_MODEL = "SIMPLE_RADIAL"

# ============================================
#            PATH RESOLUTION
# ============================================

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))

VIDEO_FOLDER = os.path.join(PROJECT_ROOT, "videos")
COLMAP_WORKSPACE = os.path.join(PROJECT_ROOT, "colmap_workspace")
OUTPUT_IMAGE_FOLDER = os.path.join(COLMAP_WORKSPACE, "images")
DATABASE_PATH = os.path.join(COLMAP_WORKSPACE, "database.db")
SPARSE_DIR = os.path.join(COLMAP_WORKSPACE, "sparse")


# ============================================
#               HELPER FUNCTIONS
# ============================================

def pick_video():
    videos = (
        glob.glob(os.path.join(VIDEO_FOLDER, "*.mp4")) +
        glob.glob(os.path.join(VIDEO_FOLDER, "*.mov")) +
        glob.glob(os.path.join(VIDEO_FOLDER, "*.avi"))
    )

    if not videos:
        raise FileNotFoundError("❌ No video files found in /videos")

    print(f"🎥 Using video: {videos[0]}")
    return videos[0]


def is_blurry(gray, threshold):
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold


def extract_frames(video_path):
    print("\n📸 Extracting frames (strict blur filtering)...")

    # Reset image directory
    if os.path.exists(OUTPUT_IMAGE_FOLDER):
        shutil.rmtree(OUTPUT_IMAGE_FOLDER)
    os.makedirs(OUTPUT_IMAGE_FOLDER, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    interval = max(1, int(fps / FRAME_RATE))

    frame_id = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if not is_blurry(gray, BLUR_THRESHOLD):
                out_path = os.path.join(OUTPUT_IMAGE_FOLDER, f"frame_{saved:05d}.jpg")
                cv2.imwrite(out_path, frame)
                saved += 1

                if saved >= MAX_FRAMES:
                    print("⚠️ Reached MAX_FRAMES limit.")
                    break

        frame_id += 1

    cap.release()
    print(f"✅ Saved {saved} sharp frames.\n")
    return saved


def run_colmap():
    print("🧭 Running COLMAP (macOS compatible)...")

    # Wipe old database
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    # ===============================
    # 1. Feature extraction
    # ===============================
    print("🔍 Step 1: Feature extraction")
    # macOS COLMAP does not support most SIFT flags → keep minimal
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", DATABASE_PATH,
        "--image_path", OUTPUT_IMAGE_FOLDER,
        "--ImageReader.camera_model", CAMERA_MODEL
    ], check=True)

    # ===============================
    # 2. Feature matching
    # ===============================
    print("🔗 Step 2: Feature matching")
    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", DATABASE_PATH
    ], check=True)

    # ===============================
    # 3. Sparse reconstruction (Mapper)
    # ===============================
    print("🗺 Step 3: Sparse reconstruction")

    if os.path.exists(SPARSE_DIR):
        shutil.rmtree(SPARSE_DIR)
    os.makedirs(SPARSE_DIR, exist_ok=True)

    subprocess.run([
        "colmap", "mapper",
        "--database_path", DATABASE_PATH,
        "--image_path", OUTPUT_IMAGE_FOLDER,
        "--output_path", SPARSE_DIR,
        "--Mapper.tri_ignore_two_view_tracks", "1",
        "--Mapper.ba_global_function_tolerance", "1e-6",
        "--Mapper.ba_global_max_refinements", "5"
    ], check=True)

    print("\n🎉 COLMAP sparse reconstruction complete!")
    print(f"📁 Results saved in: {SPARSE_DIR}")


# ============================================
#                    MAIN
# ============================================

def main():
    video_path = pick_video()
    count = extract_frames(video_path)

    if count < 10:
        print("❌ Not enough sharp frames. Lower BLUR_THRESHOLD or move camera slower.")
        return

    run_colmap()


if __name__ == "__main__":
    main()
