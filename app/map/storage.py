import json
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "cameras.json")


def save_all(cameras, edges):
    # Tạo thư mục data nếu chưa có
    os.makedirs(DATA_DIR, exist_ok=True)

    data = {
        "cameras": [cam.to_dict() for cam in cameras],
        "edges": [edge.to_dict() for edge in edges]
    }

    # Lưu file JSON
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    # Tạo thư mục riêng cho từng camera
    for cam in cameras:
        cam_folder = os.path.join(DATA_DIR, cam.id)
        os.makedirs(cam_folder, exist_ok=True)

    print("Saved cameras and created folders successfully.")
