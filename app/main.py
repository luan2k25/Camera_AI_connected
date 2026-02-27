import tkinter as tk
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import numpy as np
import time
from map.ui import MapApp
from collections import deque
import os
import json
import math


class PromptTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi Camera AI Tracking")

        self.yolo = YOLO("yolov8n.pt")

        self.cap = None
        self.running = False

        # ===== Tracking State =====
        self.target_id = None
        self.locked = False
        self.current_boxes = []

        # ===== Motion Tracking =====
        self.last_center = None
        self.exit_vector = None
        self.center_history = deque(maxlen=8)

        # ===== History =====
        self.disappear_history = []
        self.track_start_time = None
        self.frame_count = 0

        # ===== Camera System =====
        base_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(base_dir)  # đi lên 1 cấp

        self.base_camera_dir = os.path.join(base_dir, "map", "data")  # video
        self.json_data_dir = os.path.join(project_root, "data")       # cameras.json

        self.camera_positions = self.load_camera_positions()

        self.cameras = self.load_cameras()
        self.camera_positions = self.load_camera_positions()
        self.current_camera = None

        # ===== UI =====
        self.video_label = tk.Label(root)
        self.video_label.pack()
        self.video_label.bind("<Button-1>", self.on_click)

        control = tk.Frame(root)
        control.pack()

        tk.Button(control, text="Chọn Camera", command=self.select_start_camera).grid(row=0, column=0)
        tk.Button(control, text="Start", command=self.start).grid(row=0, column=1)
        tk.Button(control, text="Stop", command=self.stop).grid(row=0, column=2)
        tk.Button(control, text="Unlock", command=self.unlock).grid(row=0, column=3)
        tk.Button(control, text="Show History", command=self.show_history).grid(row=0, column=4)
        tk.Button(control, text="Maps Setting", command=self.open_maps).grid(row=0, column=5)

    # =====================================================
    # CAMERA SYSTEM
    # =====================================================

    def load_cameras(self):
        cameras = {}

        if not os.path.exists(self.base_camera_dir):
            return cameras

        for cam_name in os.listdir(self.base_camera_dir):
            cam_path = os.path.join(self.base_camera_dir, cam_name)

            if os.path.isdir(cam_path):
                for file in os.listdir(cam_path):
                    if file.endswith((".mp4", ".avi", ".mov")):
                        cameras[cam_name] = os.path.join(cam_path, file)
                        break

        return cameras

    def load_camera_positions(self):
        json_path = os.path.join(self.json_data_dir, "cameras.json")

        if not os.path.exists(json_path):
            print("cameras.json not found at:", json_path)
            return {}

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print("Error reading cameras.json:", e)
            return {}

        positions = {}
        for cam in data.get("cameras", []):
            positions[cam["id"]] = (cam["x"], cam["y"])

        print("Loaded camera positions:", positions)
        return positions


    def select_start_camera(self):
        select_window = tk.Toplevel(self.root)
        select_window.title("Chọn Camera Bắt Đầu")

        for cam_name in self.cameras.keys():
            tk.Button(
                select_window,
                text=cam_name,
                width=20,
                command=lambda name=cam_name: self.open_camera(name, select_window)
            ).pack(pady=5)

    def open_camera(self, cam_name, window=None):

        if self.cap:
            self.cap.release()

        self.current_camera = cam_name
        video_path = self.cameras.get(cam_name)

        if video_path:
            self.cap = cv2.VideoCapture(video_path)

        if window:
            window.destroy()

    # =====================================================
    # CORE LOGIC (SỬA Ở ĐÂY)
    # =====================================================

    def get_next_camera(self, frame_width, frame_height):

        if self.exit_vector is None:
            return None

        if self.current_camera not in self.camera_positions:
            return None

        current_pos = self.camera_positions[self.current_camera]

        # Normalize exit vector
        norm = math.sqrt(self.exit_vector[0] ** 2 + self.exit_vector[1] ** 2)
        if norm < 1e-6:
            return None

        exit_v = (
            self.exit_vector[0] / norm,
            self.exit_vector[1] / norm
        )

        best_cam = None
        best_score = -1

        for cam_id, pos in self.camera_positions.items():

            if cam_id == self.current_camera:
                continue

            vx = pos[0] - current_pos[0]
            vy = pos[1] - current_pos[1]

            length = math.sqrt(vx * vx + vy * vy)
            if length == 0:
                continue

            cam_vector = (vx / length, vy / length)

            # Cosine similarity
            score = exit_v[0] * cam_vector[0] + exit_v[1] * cam_vector[1]

            if score > best_score:
                best_score = score
                best_cam = cam_id

        # Ngưỡng góc tối thiểu (~ > 72 độ)
        if best_score < 0.3:
            return None

        return best_cam

    # =====================================================
    # CONTROL
    # =====================================================

    def start(self):
        if self.cap is None:
            return

        if not self.cap.isOpened():
            return

        self.running = True
        self.update_frame()

    def stop(self):
        self.running = False

    def unlock(self):
        self.locked = False
        self.target_id = None
        self.center_history.clear()
        self.exit_vector = None

    # =====================================================
    # TRACKING
    # =====================================================

    def on_click(self, event):
        x_click = event.x
        y_click = event.y

        for (x1, y1, x2, y2, obj_id) in self.current_boxes:
            if x1 <= x_click <= x2 and y1 <= y_click <= y2:
                self.target_id = obj_id
                self.locked = True
                self.track_start_time = time.time()
                self.frame_count = 0
                break

    def compute_exit_vector(self):
        if len(self.center_history) < 3:
            return None

        weights = np.arange(1, len(self.center_history))
        vectors = []

        for i in range(1, len(self.center_history)):
            v = np.array(self.center_history[i]) - np.array(self.center_history[i - 1])
            vectors.append(v)

        vectors = np.array(vectors)
        weighted = np.average(vectors, axis=0, weights=weights)

        norm = np.linalg.norm(weighted)
        if norm < 1e-6:
            return None

        return weighted / norm

    def update_frame(self):

        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.running = False
            return

        results = self.yolo.track(frame, persist=True, verbose=False)

        self.current_boxes = []
        target_found = False

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy
            ids = results[0].boxes.id
            classes = results[0].boxes.cls

            for box, obj_id, cls in zip(boxes, ids, classes):
                if self.yolo.names[int(cls)] != "person":
                    continue

                x1, y1, x2, y2 = map(int, box)
                obj_id = int(obj_id)

                self.current_boxes.append((x1, y1, x2, y2, obj_id))

                if self.locked and obj_id == self.target_id:
                    target_found = True
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    self.center_history.append((cx, cy))
                    self.frame_count += 1

                    # VẼ BOX XANH KHI LOCK
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                elif not self.locked:
                    # VẼ BOX XANH DƯƠNG KHI CHƯA LOCK
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)


        # ===== TARGET DISAPPEAR =====
        if self.locked and not target_found:

            self.exit_vector = self.compute_exit_vector()
            h, w = frame.shape[:2]
            next_cam = self.get_next_camera(w, h)

            if next_cam:

                print(f"Mục tiêu đã di chuyển từ {self.current_camera} đến {next_cam}")

                self.disappear_history.append({
                    "from": self.current_camera,
                    "to": next_cam,
                    "time": time.strftime("%H:%M:%S"),
                    "frames_tracked": self.frame_count
                })

                self.unlock()
                self.open_camera(next_cam)

                self.running = True
                self.root.after(10, self.update_frame)
                return

            else:
                self.running = False
                self.unlock()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        if self.running:
            self.root.after(10, self.update_frame)

    # =====================================================
    # UI EXTRA
    # =====================================================

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Disappearance History")

        text = tk.Text(history_window, width=80, height=20)
        text.pack()

        if not self.disappear_history:
            text.insert(tk.END, "No disappearance history.\n")
            return

        for i, entry in enumerate(self.disappear_history, 1):
            text.insert(tk.END, f"--- Event {i} ---\n")
            for key, value in entry.items():
                text.insert(tk.END, f"{key}: {value}\n")
            text.insert(tk.END, "\n")

    def open_maps(self):
        maps_window = tk.Toplevel(self.root)
        MapApp(maps_window)


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptTrackingApp(root)
    root.mainloop()
