import cv2
import os

#Ok this woks
video_path = 'videos/ghost.mp4'        
output_directory = 'extracted_frames/ghost'

start_time = 110       # Start at _ seconds
end_time = 130         # Stop at _ seconds
interval = 1          # Extract one frame every _ seconds
max_frames = None     # Optional: stop after this many frames (set None to disable)


# Create output directory
os.makedirs(output_directory, exist_ok=True)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps

print(f"Video info: {fps:.2f} FPS, {duration:.2f} seconds total")

# Clamp times to valid range
start_time = max(0, start_time)
end_time = min(duration, end_time)

# Convert time (s) to frame indices
start_frame = int(start_time * fps)
end_frame = int(end_time * fps)
interval_frames = int(interval * fps)

frame_count = start_frame
saved_count = 0

# Jump to the start time
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

while frame_count <= end_frame:
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
    ret, frame = cap.read()
    if not ret:
        break

    # Save frame
    frame_filename = os.path.join(output_directory, f'frame_{frame_count:06d}.jpg')
    cv2.imwrite(frame_filename, frame)
    saved_count += 1

    if max_frames and saved_count >= max_frames:
        break

    frame_count += interval_frames

cap.release()
cv2.destroyAllWindows()

print(f"Extracted {saved_count} frames from {start_time}s to {end_time}s (every {interval}s) into '{output_directory}'.")