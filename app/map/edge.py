class Edge:
    def __init__(self, canvas, cam1, cam2):
        self.canvas = canvas
        self.cam1 = cam1
        self.cam2 = cam2

        self.line = canvas.create_line(
            cam1.x, cam1.y,
            cam2.x, cam2.y,
            fill="green",
            width=2
        )

    def update_position(self):
        self.canvas.coords(
            self.line,
            self.cam1.x, self.cam1.y,
            self.cam2.x, self.cam2.y
        )

    def delete(self):
        self.canvas.delete(self.line)

    def to_dict(self):
        return {
            "cam1": self.cam1.id,
            "cam2": self.cam2.id
        }
