import json
import os

DATA_FILE = "data/cameras.json"

def save_all(cameras, edges):
    os.makedirs("data", exist_ok=True)

    data = {
        "cameras": [cam.to_dict() for cam in cameras],
        "edges": [edge.to_dict() for edge in edges]
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_cameras():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)
