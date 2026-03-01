import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import sys

from .camera import Camera
from .map_manager import MapManager
from . import storage
from .edge import Edge

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


class MapApp:

    # ================= INIT =================

    def __init__(self, root):
        self.root = root
        self.root.title("Camera Map System")
        self.root.geometry("1000x700")

        self.cameras = []
        self.edges = []
        self.selected_camera = None
        self.edge_mode = False
        self.edge_start = None

        self.create_ui()
        self.load_saved_map()

    # ================= UI =================

    def create_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x")

        tk.Button(top, text="Connect Cameras", command=self.toggle_edge_mode).pack(side="left", padx=5)
        tk.Button(top, text="Load Custom Map", command=self.load_map).pack(side="left", padx=5)
        tk.Button(top, text="Google Map", command=self.load_google).pack(side="left", padx=5)
        tk.Button(top, text="Add Camera", command=self.add_camera).pack(side="left", padx=5)
        tk.Button(top, text="Delete Camera", command=self.delete_camera).pack(side="left", padx=5)
        tk.Button(top, text="Save", command=self.save).pack(side="left", padx=5)
        tk.Button(top, text="Delete All", command=self.delete_all).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.select_camera)

        self.map_manager = MapManager(self.root, self.canvas)

    # ================= MAP LOAD =================

    def load_map(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if path:
            self.map_manager.load_custom_map(path)

    def load_google(self):
        self.map_manager.load_google_map()

    # ================= CAMERA =================

    def add_camera(self):
        cam = Camera(self.canvas, 200, 200)
        self.cameras.append(cam)

    def select_camera(self, event):
        item = self.canvas.find_closest(event.x, event.y)

        for cam in self.cameras:
            if cam.circle == item[0]:

                if self.edge_mode:
                    if self.edge_start is None:
                        self.edge_start = cam
                    else:
                        if self.edge_start != cam:
                            self.create_edge(self.edge_start, cam)
                        self.edge_start = None
                    return

                self.selected_camera = cam
                break

    def delete_camera(self):
        if not self.selected_camera:
            return

        # Xóa edges liên quan
        for edge in list(self.selected_camera.edges):
            edge.delete()
            self.edges.remove(edge)

            if edge.cam1 != self.selected_camera:
                edge.cam1.edges.remove(edge)
            if edge.cam2 != self.selected_camera:
                edge.cam2.edges.remove(edge)

        # Xóa folder camera
        cam_folder = resource_path(os.path.join("data", self.selected_camera.id))
        if os.path.exists(cam_folder):
            shutil.rmtree(cam_folder)

        self.selected_camera.delete()
        self.cameras.remove(self.selected_camera)
        self.selected_camera = None

    # ================= SAVE =================

    def save(self):
        try:
            # Lưu JSON
            storage.save_all(self.cameras, self.edges)

            data_dir = storage.DATA_DIR
            os.makedirs(data_dir, exist_ok=True)

            current_ids = {cam.id for cam in self.cameras}

            # Tạo folder cho từng camera
            for cam_id in current_ids:
                os.makedirs(
                    os.path.join(data_dir, cam_id),
                    exist_ok=True
                )

            # Xóa folder thừa
            for item in os.listdir(data_dir):
                path = os.path.join(data_dir, item)
                if (
                    os.path.isdir(path)
                    and item.startswith("cam")
                    and item not in current_ids
                ):
                    shutil.rmtree(path)

            messagebox.showinfo("Saved", "Data saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\n{str(e)}")


        # ================= EDGE =================

    def toggle_edge_mode(self):
        self.edge_mode = not self.edge_mode
        self.edge_start = None

    def create_edge(self, cam1, cam2):
        edge = Edge(self.canvas, cam1, cam2)
        self.edges.append(edge)
        cam1.edges.append(edge)
        cam2.edges.append(edge)

    # ================= LOAD SAVED =================

    def load_saved_map(self):

        data = storage.load_all()

        if not data:
            return

        self.canvas.delete("all")
        self.cameras.clear()
        self.edges.clear()

        Camera.counter = 1
        cam_objects = {}

        # LOAD CAMERAS
        for cam_data in data.get("cameras", []):
            cam = Camera(self.canvas, cam_data["x"], cam_data["y"])
            cam.id = cam_data["id"]
            self.canvas.itemconfig(cam.text, text=cam.id)

            self.cameras.append(cam)
            cam_objects[cam.id] = cam

        # Fix counter
        if cam_objects:
            max_id = max(int(cid[3:]) for cid in cam_objects.keys())
            Camera.counter = max_id + 1

        # LOAD EDGES
        for edge_data in data.get("edges", []):
            cam1 = cam_objects.get(edge_data["cam1"])
            cam2 = cam_objects.get(edge_data["cam2"])

            if cam1 and cam2:
                edge = Edge(self.canvas, cam1, cam2)
                self.edges.append(edge)
                cam1.edges.append(edge)
                cam2.edges.append(edge)

    # ================= DELETE ALL =================

    def delete_all(self):

        for edge in self.edges:
            edge.delete()

        for cam in self.cameras:
            cam.delete()

        self.cameras.clear()
        self.edges.clear()

        self.selected_camera = None
        self.edge_start = None
        Camera.counter = 1
        data_dir = storage.DATA_DIR
        # Xóa toàn bộ thư mục data
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)

        messagebox.showinfo("Delete All", "All cameras deleted")
