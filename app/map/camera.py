import uuid

class Camera:

    counter = 1  # biến class dùng chung

    def __init__(self, canvas, x, y):
        self.canvas = canvas

        # Tạo ID dạng cam1, cam2, cam3...
        self.id = f"cam{Camera.counter}"
        Camera.counter += 1

        self.radius = 8
        self.x = x
        self.y = y

        self.edges = []

        self.circle = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill="blue", outline="black"
        )

        self.text = canvas.create_text(
            x, y - 15,
            text=self.id,
            fill="black"
        )

        self.bind()

    def bind(self):
        self.canvas.tag_bind(self.circle, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.circle, "<B1-Motion>", self.drag)

    def start_drag(self, event):
        self.offset_x = self.x - event.x
        self.offset_y = self.y - event.y

    def drag(self, event):
        self.x = event.x + self.offset_x
        self.y = event.y + self.offset_y

        self.canvas.coords(
            self.circle,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

        self.canvas.coords(self.text, self.x, self.y - 15)

        # update edges
        for edge in self.edges:
            edge.update_position()

    def delete(self):
        self.canvas.delete(self.circle)
        self.canvas.delete(self.text)

    def to_dict(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y
        }
