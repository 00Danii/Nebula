import tkinter as tk
from tkinter import ttk, colorchooser, filedialog


class ColorSliderFrame(tk.Frame):
    def __init__(self, parent, label: str, initial: tuple[int, int, int], on_change, **kwargs):
        super().__init__(parent, **kwargs)
        self._on_change = on_change
        self._color = initial
        self._label_widget = tk.Label(self, text=label, anchor="w", width=20)
        self._label_widget.pack(side=tk.LEFT, padx=2)

        self._swatch = tk.Canvas(self, width=20, height=20, highlightthickness=1, highlightbackground="#555")
        self._swatch.pack(side=tk.LEFT, padx=4)
        self._draw_swatch()

        self._pick_btn = tk.Button(self, text="Cambiar", command=self._pick_color, width=8)
        self._pick_btn.pack(side=tk.LEFT, padx=2)

        self._r_slider = self._make_slider("R", initial[0], 0, self._on_r)
        self._g_slider = self._make_slider("G", initial[1], 1, self._on_g)
        self._b_slider = self._make_slider("B", initial[2], 2, self._on_b)

    def _make_slider(self, label, value, idx, cmd):
        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT, padx=2)
        lbl = tk.Label(frame, text=label, width=1)
        lbl.pack(side=tk.LEFT)
        var = tk.IntVar(value=value)
        slider = tk.Scale(frame, from_=0, to=255, orient=tk.HORIZONTAL,
                          variable=var, showvalue=True, width=10, length=80,
                          command=lambda v, i=idx: cmd(v, i))
        slider.pack(side=tk.LEFT)
        setattr(self, f"_var_{['r','g','b'][idx]}", var)
        return slider

    def _on_r(self, val, idx):
        self._color = (int(val), self._color[1], self._color[2])
        self._draw_swatch()
        self._on_change(self._color)

    def _on_g(self, val, idx):
        self._color = (self._color[0], int(val), self._color[2])
        self._draw_swatch()
        self._on_change(self._color)

    def _on_b(self, val, idx):
        self._color = (self._color[0], self._color[1], int(val))
        self._draw_swatch()
        self._on_change(self._color)

    def _draw_swatch(self):
        self._swatch.delete("all")
        self._swatch.create_rectangle(0, 0, 20, 20, fill=self._rgb_hex(), outline="")

    def _rgb_hex(self) -> str:
        return f"#{self._color[0]:02x}{self._color[1]:02x}{self._color[2]:02x}"

    def _pick_color(self):
        code = colorchooser.askcolor(self._rgb_hex(), title=f"Seleccionar color")
        if code and code[0]:
            r, g, b = int(code[0][0]), int(code[0][1]), int(code[0][2])
            self._color = (r, g, b)
            self._var_r.set(r)
            self._var_g.set(g)
            self._var_b.set(b)
            self._draw_swatch()
            self._on_change(self._color)

    def get_color(self) -> tuple[int, int, int]:
        return self._color

    def set_color(self, color: tuple[int, int, int]):
        self._color = color
        self._var_r.set(color[0])
        self._var_g.set(color[1])
        self._var_b.set(color[2])
        self._draw_swatch()


class ControlsPanel(tk.Frame):
    def __init__(self, parent, engine, on_render, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#2a2a2a")
        self._engine = engine
        self._on_render = on_render
        self._color_frames: dict[str, ColorSliderFrame] = {}
        self._build()

    def _build(self):
        title = tk.Label(self, text="Editor de Estilos", font=("Arial", 14, "bold"),
                         fg="white", bg="#2a2a2a")
        title.pack(pady=(10, 15))

        self._style_var = tk.StringVar()
        style_menu = ttk.Combobox(self, textvariable=self._style_var, state="readonly", width=40)
        style_menu.pack(pady=(0, 10), padx=10, fill=tk.X)
        style_menu.bind("<<ComboboxSelected>>", self._on_style_changed)
        self._style_menu = style_menu

        self._load_btn = tk.Button(self, text="Cargar Imagen", command=self._load_image,
                                   bg="#444", fg="white", relief=tk.FLAT, padx=10, pady=5)
        self._load_btn.pack(pady=(0, 10))

        self._render_btn = tk.Button(self, text="Renderizar", command=self._render,
                                     bg="#0055aa", fg="white", relief=tk.FLAT, padx=10, pady=5)
        self._render_btn.pack(pady=(0, 10))

        self._save_btn = tk.Button(self, text="Guardar Imagen", command=self._save_image,
                                   bg="#444", fg="white", relief=tk.FLAT, padx=10, pady=5)
        self._save_btn.pack(pady=(0, 10))

        sep = tk.Frame(self, height=2, bg="#555")
        sep.pack(fill=tk.X, padx=10, pady=10)

        self._colors_label = tk.Label(self, text="Colores del Estilo", font=("Arial", 11, "bold"),
                                      fg="#ccc", bg="#2a2a2a")
        self._colors_label.pack(pady=(0, 5))

        self._colors_container = tk.Frame(self, bg="#2a2a2a")
        self._colors_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self._populate_styles()

    def _populate_styles(self):
        styles = self._engine.list_styles()
        names = [s["name"] for s in styles]
        self._style_menu["values"] = names
        if names:
            current = self._engine.current_style_id
            idx = next((i for i, s in enumerate(styles) if s["id"] == current), 0)
            self._style_var.set(names[idx])
            self._show_colors(styles[idx])

    def _on_style_changed(self, event=None):
        styles = self._engine.list_styles()
        selected = self._style_var.get()
        style_info = next((s for s in styles if s["name"] == selected), None)
        if style_info:
            self._engine.set_style(style_info["id"])
            self._show_colors(style_info)

    def _show_colors(self, style_info: dict):
        for widget in self._colors_container.winfo_children():
            widget.destroy()
        self._color_frames.clear()
        for key, color in style_info["colors"].items():
            label = f"  {key.capitalize()}"
            frame = ColorSliderFrame(
                self._colors_container, label, color,
                on_change=lambda c, k=key: self._on_color_changed(k, c)
            )
            frame.pack(fill=tk.X, pady=2)
            self._color_frames[key] = frame

    def _on_color_changed(self, key: str, color: tuple[int, int, int]):
        self._engine.style_manager.update_style_color(self._engine.current_style_id, key, color)

    def _load_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("Todos", "*.*")]
        )
        if path:
            self._image_path = path

    def _render(self):
        if hasattr(self, "_image_path"):
            self._on_render(self._image_path)
        else:
            from tkinter import messagebox
            messagebox.showwarning("Sin imagen", "Carga una imagen primero.")

    def _save_image(self):
        from tkinter import messagebox
        path = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos", "*.*")]
        )
        if path:
            if hasattr(self, "_last_result") and self._last_result:
                self._last_result.save(path)
                messagebox.showinfo("Guardado", f"Imagen guardada en:\n{path}")

    def set_result(self, image):
        self._last_result = image
