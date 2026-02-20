from PIL import Image, ImageTk
from tkinterweb import HtmlFrame

class MapManager:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas
        self.browser = None
        self.map_image = None

    def load_custom_map(self, file_path):
        img = Image.open(file_path)
        img = img.resize((1000, 650))
        self.map_image = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.map_image)

    def load_google_map(self):
        self.canvas.pack_forget()
        self.browser = HtmlFrame(self.root)
        self.browser.pack(fill="both", expand=True)
        self.browser.load_website("https://www.google.com/maps")
