import cv2
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from shapely.ops import unary_union, linemerge
from shapely.geometry import MultiLineString


# STEP 1 — LOAD + PREPROCESS
image_path = "room.png"
img = cv2.imread(image_path)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)

# STEP 2 — detect line segments using HoughLinesP
lines = cv2.HoughLinesP(
    edges,
    rho=1,
    theta=np.pi/180,
    threshold=80,
    minLineLength=50,
    maxLineGap=15
)

if lines is None:
    raise Exception("No lines detected.")


# STEP 3 — MERGE + CLEAN LINES USING SHAPELY
line_segments = []

for line in lines:
    x1, y1, x2, y2 = line[0]
    line_segments.append(LineString([(x1, y1), (x2, y2)]))

# Combine touching/overlapping segments
merged = linemerge(unary_union(line_segments))

# Ensure list format
if isinstance(merged, LineString):
    merged = [merged]                       # single line
elif isinstance(merged, MultiLineString):
    merged = list(merged.geoms)             # extract all lines
else:
    merged = []                             # fallback


# STEP 4 — create a blank white canvas using Pillow
h, w = gray.shape
canvas = Image.new("RGB", (w, h), "white")
draw = ImageDraw.Draw(canvas)

# STEP 5 — draw the wall lines
for line in lines:
    x1, y1, x2, y2 = line[0]
    
    # black lines, width=3 px
    draw.line([(x1, y1), (x2, y2)], fill="black", width=3)

# STEP 6 — save result
canvas.save("room_layout_pillow.png")
canvas.show()