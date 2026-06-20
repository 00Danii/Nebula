import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image

from core.engine import RenderEngine
from ui.canvas import ImageCanvas
from ui.controls import ControlsPanel


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Análisis Visual Científico-Técnico")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        self.configure(bg="#1a1a1a")

        self._engine = RenderEngine()

        self._build_layout()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        self._canvas = ImageCanvas(self, width=800, height=800)
        self._canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self._controls = ControlsPanel(self, self._engine, on_render=self._do_render)
        self._controls.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))

    def _do_render(self, image_path: str):
        try:
            self.config(cursor="watch")
            self.update()
            result = self._engine.render(image_path)
            self._canvas.display(result)
            self._controls.set_result(result)
            self.config(cursor="")
        except Exception as e:
            self.config(cursor="")
            messagebox.showerror("Error de Renderizado", f"Ocurrió un error:\n{e}")

    def _on_close(self):
        self.destroy()
