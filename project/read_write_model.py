# Copyright (c) 2017, ETH Zurich and UNC Chapel Hill.
# All rights reserved.

import struct
import collections
import numpy as np


CameraModel = collections.namedtuple(
    "CameraModel", ["model_id", "model_name", "num_params"]
)

Camera = collections.namedtuple(
    "Camera", ["id", "model", "width", "height", "params"]
)

Image = collections.namedtuple(
    "Image",
    [
        "id", "qvec", "tvec", "camera_id", "name", "xys", "point3D_ids"
    ]
)

Point3D = collections.namedtuple(
    "Point3D", ["id", "xyz", "rgb", "error", "image_ids", "point2D_idxs"]
)


# -----------------------------------------------------------------------------
# Camera models
# -----------------------------------------------------------------------------

# From COLMAP's source code (colmap/src/base/camera_models.h)
CAMERA_MODELS = {
    0: CameraModel(0, "SIMPLE_PINHOLE", 3),
    1: CameraModel(1, "PINHOLE", 4),
    2: CameraModel(2, "SIMPLE_RADIAL", 4),
    3: CameraModel(3, "RADIAL", 5),
    4: CameraModel(4, "OPENCV", 8),
    5: CameraModel(5, "OPENCV_FISHEYE", 8),
    6: CameraModel(6, "FULL_OPENCV", 12),
    7: CameraModel(7, "FOV", 5),
    8: CameraModel(8, "SIMPLE_RADIAL_FISHEYE", 4),
    9: CameraModel(9, "RADIAL_FISHEYE", 5),
    10: CameraModel(10, "THIN_PRISM_FISHEYE", 12),
}


def read_next_bytes(fid, num_bytes, format_char_sequence, endian_character="<"):
    data = fid.read(num_bytes)
    return struct.unpack(endian_character + format_char_sequence, data)


# -----------------------------------------------------------------------------
# Read Cameras
# -----------------------------------------------------------------------------

def read_cameras_binary(path_to_model_file):
    cameras = {}
    with open(path_to_model_file, "rb") as fid:
        num_cameras = read_next_bytes(fid, 8, "Q")[0]
        for _ in range(num_cameras):
            camera_properties = read_next_bytes(fid, 24, "iiQQ")
            camera_id = camera_properties[0]
            model_id = camera_properties[1]
            width = camera_properties[2]
            height = camera_properties[3]

            camera_model = CAMERA_MODELS[model_id]
            num_params = camera_model.num_params

            params = read_next_bytes(fid, 8 * num_params, "d" * num_params)
            cameras[camera_id] = Camera(
                id=camera_id,
                model=camera_model.model_name,
                width=width,
                height=height,
                params=np.array(params),
            )
    return cameras


# -----------------------------------------------------------------------------
# Read Images
# -----------------------------------------------------------------------------

def read_images_binary(path):
    images = {}
    with open(path, "rb") as fid:
        num_images = read_next_bytes(fid, 8, "Q")[0]
        for _ in range(num_images):
            binary_image_properties = read_next_bytes(fid, 64, "idddddddiQ")
            image_id = binary_image_properties[0]
            qvec = np.array(binary_image_properties[1:5])
            tvec = np.array(binary_image_properties[5:8])
            camera_id = binary_image_properties[8]
            name_length = binary_image_properties[9]

            name = fid.read(name_length).decode("utf-8")

            num_points2D = read_next_bytes(fid, 8, "Q")[0]

            xys = np.zeros((num_points2D, 2))
            point3D_ids = np.zeros(num_points2D, dtype=np.int64)

            for i in range(num_points2D):
                xy = read_next_bytes(fid, 16, "dd")
                pid = read_next_bytes(fid, 8, "q")[0]
                xys[i] = xy
                point3D_ids[i] = pid

            images[image_id] = Image(
                id=image_id,
                qvec=qvec,
                tvec=tvec,
                camera_id=camera_id,
                name=name,
                xys=xys,
                point3D_ids=point3D_ids,
            )
    return images


# -----------------------------------------------------------------------------
# Read Points3D
# -----------------------------------------------------------------------------

def read_points3d_binary(path):
    points3D = {}
    with open(path, "rb") as fid:
        num_points = read_next_bytes(fid, 8, "Q")[0]

        for _ in range(num_points):
            point_id = read_next_bytes(fid, 8, "Q")[0]
            xyz = np.array(read_next_bytes(fid, 24, "ddd"))
            rgb = np.array(read_next_bytes(fid, 12, "BBB"))
            error = read_next_bytes(fid, 8, "d")[0]

            track_length = read_next_bytes(fid, 8, "Q")[0]
            image_ids = []
            point2D_idxs = []

            for _ in range(track_length):
                image_id = read_next_bytes(fid, 8, "Q")[0]
                point2D_idx = read_next_bytes(fid, 8, "Q")[0]
                image_ids.append(image_id)
                point2D_idxs.append(point2D_idx)

            points3D[point_id] = Point3D(
                id=point_id,
                xyz=xyz,
                rgb=rgb,
                error=error,
                image_ids=np.array(image_ids),
                point2D_idxs=np.array(point2D_idxs),
            )

    return points3D


# -----------------------------------------------------------------------------
# Unified API
# -----------------------------------------------------------------------------

def read_cameras(path):
    if path.endswith(".bin"):
        return read_cameras_binary(path)
    raise ValueError("Unsupported camera file format.")

def read_images(path):
    if path.endswith(".bin"):
        return read_images_binary(path)
    raise ValueError("Unsupported image file format.")

def read_points3d(path):
    if path.endswith(".bin"):
        return read_points3d_binary(path)
    raise ValueError("Unsupported points3D file format.")
