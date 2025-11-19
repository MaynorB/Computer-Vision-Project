import cv2
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from shapely.ops import unary_union, linemerge


# ------------------------------------------------------------
# STEP 1 — LOAD + PREPROCESS
# ------------------------------------------------------------
image_path = "room.png"
img = cv2.imread(image_path)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)


# ------------------------------------------------------------
# STEP 2 — DETECT LINE SEGMENTS (walls)
# ------------------------------------------------------------
lines = cv2.HoughLinesP(
    edges,
    rho=1,
    theta=np.pi/180,
    threshold=80,
    minLineLength=50,
    maxLineGap=15
)

if lines is None:
    raise ValueError("No lines detected — try adjusting parameters or using a clearer image.")


# ------------------------------------------------------------
# STEP 3 — MERGE + CLEAN LINES USING SHAPELY
# ------------------------------------------------------------
line_segments = []

for line in lines:
    x1, y1, x2, y2 = line[0]
    line_segments.append(LineString([(x1, y1), (x2, y2)]))

# Combine touching/overlapping segments
merged = linemerge(unary_union(line_segments))

# Ensure list format
if isinstance(merged, LineString):
    merged = [merged]
else:
    merged = list(merged)


# ------------------------------------------------------------
# STEP 4 — DRAW 2D LAYOUT
# ------------------------------------------------------------
plt.figure(figsize=(8, 8))

for line in merged:
    x, y = line.xy
    plt.plot(x, y, linewidth=2, color="black")

plt.gca().set_aspect("equal", adjustable="box")
plt.gca().invert_yaxis()   # Match image coordinate system
plt.title("2D Room Layout (Wall Lines)")
plt.xlabel("x")
plt.ylabel("y")
plt.show()