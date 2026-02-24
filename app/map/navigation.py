from typing import Dict, List, Tuple, Optional
import numpy as np


class CameraGraph:
    def __init__(self):
        self.positions: Dict[str, Tuple[float, float]] = {}
        self.adj: Dict[str, List[str]] = {}

    def add_camera(self, cam_id: str, x: float, y: float):
        self.positions[cam_id] = (x, y)
        self.adj.setdefault(cam_id, [])

    def add_connection(self, cam1: str, cam2: str):
        self.adj[cam1].append(cam2)
        self.adj[cam2].append(cam1)

    def load_from_json(self, config: dict):
        # Add cameras
        for cam in config["cameras"]:
            self.add_camera(cam["id"], cam["x"], cam["y"])

        # Add edges
        for edge in config["edges"]:
            self.add_connection(edge["cam1"], edge["cam2"])


class DirectionRouter:
    def __init__(self, graph: CameraGraph):
        self.graph = graph

    def next_camera(
        self,
        current_cam: str,
        direction: np.ndarray
    ) -> Optional[str]:

        if direction is None:
            return None

        dx_dir, dy_dir = direction
        best_score = -1
        best_cam = None

        xi, yi = self.graph.positions[current_cam]

        for neighbor in self.graph.adj[current_cam]:
            xj, yj = self.graph.positions[neighbor]

            dx = xj - xi
            dy = yj - yi

            dot = dx * dx_dir + dy * dy_dir

            if dot <= 0:
                continue

            len2 = dx * dx + dy * dy
            score = (dot * dot) / len2

            if score > best_score:
                best_score = score
                best_cam = neighbor

        return best_cam
