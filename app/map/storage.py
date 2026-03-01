import json
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)



def get_data_dir():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(".")
    return os.path.join(base_dir, "data")

DATA_DIR = get_data_dir()
DATA_FILE = os.path.join(DATA_DIR, "cameras.json")




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
