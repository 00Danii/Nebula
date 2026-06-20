import tkinter as tk
from PIL import Image, ImageTk


class ImageCanvas(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#1a1a1a")
        self._label = tk.Label(self, bg="#1a1a1a")
        self._label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self._photo: ImageTk.PhotoImage | None = None
        self._image: Image.Image | None = None

    def display(self, image: Image.Image):
        self._image = image
        max_w = self.winfo_width() - 20 if self.winfo_width() > 100 else 800
        max_h = self.winfo_height() - 20 if self.winfo_height() > 100 else 800
        display_img = image.copy()
        display_img.thumbnail((max_w, max_h), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(display_img)
        self._label.config(image=self._photo)

    def get_image(self) -> Image.Image | None:
        return self._image
