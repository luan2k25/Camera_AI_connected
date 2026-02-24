import tkinter as tk
from tkinter import filedialog, messagebox
from .camera import Camera
from .map_manager import MapManager
from . import storage
from .edge import Edge




class MapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Map System")
        self.root.geometry("1000x700")

        self.cameras = []
        self.selected_camera = None

        self.create_ui()

        self.edges = []
        self.edge_mode = False
        self.edge_start = None


    def create_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x")
        tk.Button(top, text="Connect Cameras", command=self.toggle_edge_mode).pack(side="left", padx=5)

        tk.Button(top, text="Load Custom Map", command=self.load_map).pack(side="left", padx=5)
        tk.Button(top, text="Google Map", command=self.load_google).pack(side="left", padx=5)
        tk.Button(top, text="Add Camera", command=self.add_camera).pack(side="left", padx=5)
        tk.Button(top, text="Delete Camera", command=self.delete_camera).pack(side="left", padx=5)
        tk.Button(top, text="Save", command=self.save).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.select_camera)

        self.map_manager = MapManager(self.root, self.canvas)

    def load_map(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if path:
            self.map_manager.load_custom_map(path)

    def load_google(self):
        self.map_manager.load_google_map()

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
        if self.selected_camera:

            # Xóa edges liên quan
            for edge in list(self.selected_camera.edges):
                edge.delete()
                self.edges.remove(edge)

                if edge.cam1 != self.selected_camera:
                    edge.cam1.edges.remove(edge)
                if edge.cam2 != self.selected_camera:
                    edge.cam2.edges.remove(edge)

            self.selected_camera.delete()
            self.cameras.remove(self.selected_camera)
            self.selected_camera = None

    def save(self):
        storage.save_all(self.cameras, self.edges)
        messagebox.showinfo("Saved", "Data saved")



    def toggle_edge_mode(self):
        self.edge_mode = not self.edge_mode
        self.edge_start = None
    def create_edge(self, cam1, cam2):
        edge = Edge(self.canvas, cam1, cam2)
        self.edges.append(edge)

        cam1.edges.append(edge)
        cam2.edges.append(edge)
