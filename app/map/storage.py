import json
import os

# Thư mục và file cố định
DATA_DIR = "data"
DATA_FILE = "data/cameras.json"


def save_all(cameras, edges):
    """
    Lưu toàn bộ cameras và edges vào data/cameras.json
    """

    # Đảm bảo thư mục tồn tại
    os.makedirs(DATA_DIR, exist_ok=True)

    data = {
        "cameras": [cam.to_dict() for cam in cameras],
        "edges": [edge.to_dict() for edge in edges]
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_all():
    """
    Load toàn bộ dữ liệu từ data/cameras.json
    """

    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def delete_data_file():
    """
    Xóa file cameras.json nếu tồn tại
    """

    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
