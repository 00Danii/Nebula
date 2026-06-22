import tkinter as tk
from tkinter import messagebox

from core.engine import RenderEngine
from ui.canvas import ImageCanvas
from ui.controls import ControlsPanel
import ui.theme as th


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Analisis Visual Cientifico-Tecnico")
        self.attributes("-fullscreen", True)
        self.configure(bg=th.BG_DARK)

        self._engine = RenderEngine()

        self._build_titlebar()
        self._build_layout()
        self._bind_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=th.BG_MEDIUM, bd=0)
        bar.pack(fill=tk.X, side=tk.TOP)

        title = tk.Label(bar, text="Editor de Analisis Visual Cientifico-Tecnico",
                         font=(th.FONT_FAMILY, 10), bg=th.BG_MEDIUM, fg=th.FG_DIM)
        title.pack(side=tk.LEFT, padx=8, pady=4)

        btn_frame = tk.Frame(bar, bg=th.BG_MEDIUM)
        btn_frame.pack(side=tk.RIGHT, padx=4)

        self._min_btn = tk.Button(btn_frame, text="\u2014",
                                  font=(th.FONT_FAMILY, 12),
                                  bg=th.BG_MEDIUM, fg=th.FG,
                                  activebackground=th.BG_LIGHT, activeforeground=th.FG_BRIGHT,
                                  relief=tk.FLAT, bd=0, highlightthickness=0,
                                  padx=10, pady=2, command=self._on_minimize)
        self._min_btn.pack(side=tk.LEFT, padx=1)

        self._close_btn = tk.Button(btn_frame, text="\u2715",
                                    font=(th.FONT_FAMILY, 11),
                                    bg=th.BG_MEDIUM, fg=th.FG,
                                    activebackground="#e81123", activeforeground="#ffffff",
                                    relief=tk.FLAT, bd=0, highlightthickness=0,
                                    padx=10, pady=2, command=self._on_close)
        self._close_btn.pack(side=tk.LEFT, padx=1)

    def _build_layout(self):
        body = tk.Frame(self, bg=th.BG_DARK)
        body.pack(fill=tk.BOTH, expand=True)

        self._canvas = ImageCanvas(body)
        self._canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self._controls = ControlsPanel(body, self._engine, on_render=self._do_render)
        self._controls.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))

    def _bind_shortcuts(self):
        self.bind("<Escape>", lambda e: self._on_close())
        self.bind("<Control-o>", lambda e: self._controls.load_image())
        self.bind("<Control-s>", lambda e: self._controls.save_image())
        self.bind("<Control-z>", lambda e: self._controls.undo())
        self.bind("<Control-y>", lambda e: self._controls.redo())
        self.bind("<Control-r>", lambda e: self._controls.clear_all())
        self.bind("<Control-q>", lambda e: self._on_close())

    def _do_render(self, image_path: str | None):
        if not image_path:
            self._canvas.clear()
            return
        try:
            self.config(cursor="watch")
            self.update()
            result = self._engine.render(image_path)
            self._canvas.display(result, self._engine.original_image)
            self._controls.set_result(result)
            self.config(cursor="")
        except Exception as e:
            self.config(cursor="")
            messagebox.showerror("Error", f"Ocurrio un error:\n{e}")

    def _on_minimize(self):
        self.iconify()

    def _on_close(self):
        self.destroy()
