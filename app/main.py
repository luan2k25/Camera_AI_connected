import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import numpy as np
import time
from map.ui import MapApp


class PromptTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Click Target Tracking")

        self.yolo = YOLO("yolov8n.pt")

        self.cap = None
        self.running = False

        # Tracking state
        self.target_id = None
        self.locked = False
        self.current_boxes = []

        # Motion tracking
        self.prev_center = None
        self.last_center = None
        self.exit_vector = None  # ← BIẾN HƯỚNG RỜI KHỎI

        # UI
        self.video_label = tk.Label(root)
        self.video_label.pack()
        self.video_label.bind("<Button-1>", self.on_click)


        #History storage
        self.disappear_history = []

        #Tracking Time
        self.track_start_time = None
        self.frame_count = 0

        control = tk.Frame(root)
        control.pack()


        #Button
        tk.Button(control, text="Mở Video", command=self.open_video).grid(row=0, column=0)
        tk.Button(control, text="Webcam", command=self.open_webcam).grid(row=0, column=1)
        tk.Button(control, text="Start", command=self.start).grid(row=0, column=2)
        tk.Button(control, text="Stop", command=self.stop).grid(row=0, column=3)
        tk.Button(control, text="Unlock", command=self.unlock).grid(row=0, column=4)
        tk.Button(control, text="Show History", command=self.show_history).grid(row=0, column=5)
        tk.Button(control, text="Maps Setting", command=self.open_maps).grid(row=0, column=6)

    def open_video(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.cap = cv2.VideoCapture(file_path)

    def open_webcam(self):
        self.cap = cv2.VideoCapture(0)

    def start(self):
        self.running = True
        self.update_frame()

    def stop(self):
        self.running = False

    def unlock(self):
        self.locked = False
        self.target_id = None
        self.prev_center = None
        self.last_center = None

    def on_click(self, event):
        x_click = event.x
        y_click = event.y

        for (x1, y1, x2, y2, obj_id) in self.current_boxes:
            if x1 <= x_click <= x2 and y1 <= y_click <= y2:
                self.target_id = obj_id
                self.locked = True
                self.track_start_time = time.time()
                self.frame_count = 0
                print(f"Locked ID: {obj_id}")
                break

    def compute_exit_vector(self): #Đọc hướng rời khỏi camera
        if self.prev_center is None or self.last_center is None:
            return None

        v = np.array(self.last_center) - np.array(self.prev_center)
        norm = np.linalg.norm(v)

        if norm == 0:
            return None

        return v / norm  # vector đơn vị

    def update_frame(self): #Vẽ frame liên tục
        if self.running and self.cap:
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

                        self.prev_center = self.last_center
                        self.last_center = (cx, cy)

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                        self.frame_count += 1

                    elif not self.locked:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # Nếu target biến mất
            if self.locked and not target_found:
                self.exit_vector = self.compute_exit_vector()

                disappear_time = time.time()
                duration = disappear_time - self.track_start_time if self.track_start_time else 0

                history_entry = {
                    "target_id": self.target_id,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(disappear_time)),
                    "duration": round(duration, 2),
                    "last_position": self.last_center,
                    "exit_vector": self.exit_vector.tolist() if self.exit_vector is not None else None,
                    "frames_tracked": self.frame_count
                }

                self.disappear_history.append(history_entry)

                print("Saved history:", history_entry)

                self.running = False
                self.unlock()


            # Hiển thị frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            if self.running:
                self.root.after(10, self.update_frame)

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
            text.insert(tk.END, f"Target ID: {entry['target_id']}\n")
            text.insert(tk.END, f"Time: {entry['time']}\n")
            text.insert(tk.END, f"Duration: {entry['duration']} sec\n")
            text.insert(tk.END, f"Frames Tracked: {entry['frames_tracked']}\n")
            text.insert(tk.END, f"Last Position: {entry['last_position']}\n")
            text.insert(tk.END, f"Exit Vector: {entry['exit_vector']}\n\n")
    #Mở map
    def open_maps(self):
        maps_window = tk.Toplevel(self.root)
        MapApp(maps_window)




if __name__ == "__main__":
    root = tk.Tk()
    app = PromptTrackingApp(root)
    root.mainloop()
