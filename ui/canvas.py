import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

import ui.theme as th


class ImageCanvas(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=th.BG_DARK)
        self._label = tk.Label(self, bg=th.BG_DARK)
        self._label.pack(expand=True, fill=tk.BOTH, padx=4, pady=4)
        self._photo: ImageTk.PhotoImage | None = None
        self._image: Image.Image | None = None

    def display(self, image: Image.Image, original: Image.Image | None = None):
        self._image = image
        max_w = self.winfo_width() - 8 if self.winfo_width() > 100 else 800
        max_h = self.winfo_height() - 8 if self.winfo_height() > 100 else 800
        display_img = image.copy()
        display_img.thumbnail((max_w, max_h), Image.LANCZOS)

        if original is not None:
            preview = original.copy()
            preview.thumbnail((100, 100), Image.LANCZOS)
            pw, ph = preview.size
            pos_x = display_img.width - pw - 8
            pos_y = display_img.height - ph - 8
            overlay = Image.new("RGBA", display_img.size, (0, 0, 0, 0))
            overlay.paste(preview, (pos_x, pos_y))
            draw_overlay = ImageDraw.Draw(overlay)
            draw_overlay.rectangle(
                [pos_x - 1, pos_y - 1, pos_x + pw + 1, pos_y + ph + 1],
                outline=th.ACCENT, width=1
            )
            display_img = Image.alpha_composite(display_img.convert("RGBA"), overlay).convert("RGB")

        self._photo = ImageTk.PhotoImage(display_img)
        self._label.config(image=self._photo)

    def clear(self):
        self._image = None
        self._photo = None
        self._label.config(image="")

    def get_image(self) -> Image.Image | None:
        return self._image
