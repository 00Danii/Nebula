import os
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox

import ui.theme as th


class ModernButton(tk.Button):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("font", (th.FONT_FAMILY, 10))
        kwargs.setdefault("bg", th.BTN_BG)
        kwargs.setdefault("fg", th.FG)
        kwargs.setdefault("activebackground", th.BTN_HOVER)
        kwargs.setdefault("activeforeground", th.FG_BRIGHT)
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("padx", 12)
        kwargs.setdefault("pady", 6)
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", lambda e: self.configure(bg=th.BTN_HOVER))
        self.bind("<Leave>", lambda e: self.configure(bg=th.BTN_BG))


class Section(tk.Frame):
    def __init__(self, parent, title: str, expanded: bool = True, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, **kwargs)
        self._expanded = expanded
        self._content_frame: tk.Frame | None = None

        header = tk.Frame(self, bg=th.SECTION_BG)
        header.pack(fill=tk.X)

        self._toggle_btn = tk.Button(
            header,
            text=f"\u25bc {title}" if expanded else f"\u25b6 {title}",
            font=(th.FONT_FAMILY, 10, "bold"),
            bg=th.SECTION_BG, fg=th.FG,
            activebackground=th.BG_LIGHT, activeforeground=th.FG_BRIGHT,
            relief=tk.FLAT, bd=0, anchor="w",
            padx=8, pady=4,
            command=self._toggle,
        )
        self._toggle_btn.pack(fill=tk.X)

        self._container = tk.Frame(self, bg=th.BG_DARK)
        if expanded:
            self._container.pack(fill=tk.X, padx=0, pady=(0, 4))

    def _toggle(self):
        self._expanded = not self._expanded
        self._toggle_btn.config(
            text=f"\u25bc {self._toggle_btn.cget('text')[1:].strip()}" if self._expanded
            else f"\u25b6 {self._toggle_btn.cget('text')[1:].strip()}"
        )
        if self._expanded:
            self._container.pack(fill=tk.X, padx=0, pady=(0, 4))
        else:
            self._container.pack_forget()

    @property
    def container(self) -> tk.Frame:
        return self._container


class AdjustmentSlider(tk.Frame):
    def __init__(self, parent, label: str, from_: int, to: int,
                 initial: float, resolution: float,
                 value_label: str, on_change, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, **kwargs)
        self._on_change = on_change
        self._value_label_fmt = value_label

        row = tk.Frame(self, bg=th.BG_DARK)
        row.pack(fill=tk.X, padx=8, pady=1)

        lbl = tk.Label(row, text=label, font=(th.FONT_FAMILY, 9),
                       bg=th.BG_DARK, fg=th.FG, anchor="w", width=14)
        lbl.pack(side=tk.LEFT)

        self._var = tk.DoubleVar(value=initial)
        slider = tk.Scale(row, from_=from_, to=to, orient=tk.HORIZONTAL,
                          variable=self._var, showvalue=False,
                          resolution=resolution,
                          width=10, length=140,
                          bg=th.BG_DARK, fg=th.FG, troughcolor=th.SLIDER_TROUGH,
                          activebackground=th.ACCENT, highlightthickness=0,
                          bd=0, sliderrelief=tk.FLAT)
        slider.pack(side=tk.LEFT, padx=(4, 4), expand=True, fill=tk.X)

        self._val_label = tk.Label(row, text=value_label % initial,
                                   font=(th.FONT_FAMILY, 9),
                                   bg=th.BG_DARK, fg=th.FG_DIM, anchor="e", width=6)
        self._val_label.pack(side=tk.RIGHT)

        slider.bind("<ButtonRelease-1>", lambda e: self._notify())
        slider.bind("<Motion>", lambda e: self._update_label())

        self._notify()

    def _update_label(self):
        val = self._var.get()
        self._val_label.config(text=self._value_label_fmt % val)

    def _notify(self):
        self._update_label()
        self._on_change(self._var.get())

    def get_value(self) -> float:
        return self._var.get()

    def set_value(self, value: float):
        self._var.set(value)
        self._update_label()


class ColorRow(tk.Frame):
    def __init__(self, parent, label: str, initial: tuple[int, int, int],
                 on_change, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, **kwargs)
        self._on_change = on_change
        self._color = initial

        lbl = tk.Label(self, text=label, font=(th.FONT_FAMILY, 9),
                       bg=th.BG_DARK, fg=th.FG, anchor="w", width=14)
        lbl.pack(side=tk.LEFT, padx=8)

        self._swatch = tk.Canvas(self, width=18, height=18,
                                 highlightthickness=1, highlightbackground=th.BORDER,
                                 bg=th.BG_DARK, bd=0)
        self._swatch.pack(side=tk.LEFT, padx=(0, 6))
        self._draw_swatch()

        pick_btn = tk.Button(self, text="\u25cf", font=(th.FONT_FAMILY, 9),
                             bg=th.BTN_BG, fg=th.FG,
                             activebackground=th.BTN_HOVER, activeforeground=th.FG_BRIGHT,
                             relief=tk.FLAT, bd=0, padx=4, pady=0,
                             command=self._pick)
        pick_btn.pack(side=tk.LEFT)

        self._var_r = tk.IntVar(value=initial[0])
        self._var_g = tk.IntVar(value=initial[1])
        self._var_b = tk.IntVar(value=initial[2])

        for name, var in [("R", self._var_r), ("G", self._var_g), ("B", self._var_b)]:
            f = tk.Frame(self, bg=th.BG_DARK)
            f.pack(side=tk.LEFT, padx=1)
            c_lbl = tk.Label(f, text=name, font=(th.FONT_FAMILY, 8),
                             bg=th.BG_DARK, fg=th.FG_DIM)
            c_lbl.pack(side=tk.LEFT)
            s = tk.Scale(f, from_=0, to=255, orient=tk.HORIZONTAL,
                         variable=var, showvalue=False,
                         width=6, length=45,
                         bg=th.BG_DARK, fg=th.FG, troughcolor=th.SLIDER_TROUGH,
                         activebackground=th.ACCENT, highlightthickness=0,
                         bd=0, sliderrelief=tk.FLAT)
            s.pack(side=tk.LEFT)
            s.bind("<ButtonRelease-1>", lambda e, i=name.lower(): self._on_slider(i))

    def _draw_swatch(self):
        self._swatch.delete("all")
        self._swatch.create_rectangle(0, 0, 18, 18, fill=self._rgb_hex(), outline="")

    def _rgb_hex(self) -> str:
        return f"#{self._color[0]:02x}{self._color[1]:02x}{self._color[2]:02x}"

    def _on_slider(self, channel: str):
        self._color = (self._var_r.get(), self._var_g.get(), self._var_b.get())
        self._draw_swatch()
        self._on_change(self._color)

    def _pick(self):
        code = colorchooser.askcolor(self._rgb_hex(), title="Seleccionar color")
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
        self.configure(bg=th.BG_DARK)
        self._engine = engine
        self._on_render = on_render
        self._color_rows: dict[str, ColorRow] = {}
        self._adj_sliders: dict[str, AdjustmentSlider] = {}
        self._image_path: str | None = None
        self._render_after_id: int | None = None
        self._build()

    def _build(self):
        canvas = tk.Canvas(self, bg=th.BG_DARK, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview,
                                 bg=th.BG_MEDIUM, troughcolor=th.BG_DARK,
                                 activebackground=th.BG_LIGHT)
        scroll_frame = tk.Frame(canvas, bg=th.BG_DARK)

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._scroll_canvas = canvas
        self._scroll_frame = scroll_frame

        self._build_content(scroll_frame)

    def _build_content(self, parent):
        header = tk.Frame(parent, bg=th.BG_MEDIUM)
        header.pack(fill=tk.X, pady=(0, 8))
        title = tk.Label(header, text="Editor de Imagen",
                         font=(th.FONT_FAMILY, 13, "bold"),
                         bg=th.BG_MEDIUM, fg=th.FG_BRIGHT, padx=10, pady=8)
        title.pack()

        file_sec = Section(parent, "Archivo", expanded=True)
        file_sec.pack(fill=tk.X, pady=(0, 4))
        fc = file_sec.container

        self._load_btn = ModernButton(fc, text="Cargar Imagen  [Ctrl+O]",
                                       command=self._load_image)
        self._load_btn.pack(fill=tk.X, padx=8, pady=2)

        self._save_btn = ModernButton(fc, text="Guardar Resultado  [Ctrl+S]",
                                       command=self._save_image)
        self._save_btn.pack(fill=tk.X, padx=8, pady=2)

        adj_sec = Section(parent, "Ajustes de Imagen", expanded=True)
        adj_sec.pack(fill=tk.X, pady=(0, 4))
        ac = adj_sec.container

        self._build_adjustments(ac)

        reset_btn = tk.Button(ac, text="Restablecer ajustes",
                              font=(th.FONT_FAMILY, 9),
                              bg=th.BG_LIGHT, fg=th.FG_DIM,
                              activebackground=th.BTN_HOVER, activeforeground=th.FG,
                              relief=tk.FLAT, bd=0, padx=8, pady=3,
                              command=self._reset_adjustments)
        reset_btn.pack(pady=(4, 2))

        style_sec = Section(parent, "Estilo de Color", expanded=True)
        style_sec.pack(fill=tk.X, pady=(0, 4))
        sc = style_sec.container

        self._style_var = tk.StringVar()
        self._style_menu = ttk.Combobox(sc, textvariable=self._style_var,
                                         state="readonly", width=30,
                                         font=(th.FONT_FAMILY, 10))
        self._style_menu.pack(fill=tk.X, padx=8, pady=4)
        self._style_menu.bind("<<ComboboxSelected>>", self._on_style_changed)

        style_style = ttk.Style()
        style_style.theme_use("clam")
        style_style.configure("TCombobox",
                              fieldbackground=th.BG_INPUT,
                              background=th.BG_LIGHT,
                              foreground=th.FG,
                              arrowcolor=th.FG,
                              selectbackground=th.ACCENT,
                              selectforeground=th.FG_BRIGHT)

        self._colors_container = tk.Frame(sc, bg=th.BG_DARK)
        self._colors_container.pack(fill=tk.X, padx=0, pady=(0, 4))

        theme_sec = Section(parent, "Apariencia", expanded=True)
        theme_sec.pack(fill=tk.X, pady=(0, 4))
        tc = theme_sec.container

        row = tk.Frame(tc, bg=th.BG_DARK)
        row.pack(fill=tk.X, padx=8, pady=2)
        lbl = tk.Label(row, text="Color de acento", font=(th.FONT_FAMILY, 9),
                       bg=th.BG_DARK, fg=th.FG, anchor="w", width=14)
        lbl.pack(side=tk.LEFT)
        self._theme_swatch = tk.Canvas(row, width=18, height=18,
                                       highlightthickness=1, highlightbackground=th.BORDER,
                                       bg=th.BG_DARK, bd=0)
        self._theme_swatch.pack(side=tk.LEFT, padx=4)
        self._draw_theme_swatch()
        theme_btn = tk.Button(row, text="Cambiar", font=(th.FONT_FAMILY, 9),
                              bg=th.BTN_BG, fg=th.FG,
                              activebackground=th.BTN_HOVER, activeforeground=th.FG_BRIGHT,
                              relief=tk.FLAT, bd=0, padx=8, pady=1,
                              command=self._pick_accent)
        theme_btn.pack(side=tk.LEFT, padx=4)

        # Status bar
        status_bar = tk.Frame(self, bg=th.BG_DARK, bd=0)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._status_label = tk.Label(status_bar, text="Listo",
                                      font=(th.FONT_FAMILY, 9),
                                      bg=th.BG_DARK, fg=th.FG_DIM,
                                      anchor="w", padx=10, pady=4)
        self._status_label.pack(fill=tk.X)

        self._populate_styles()

    def _build_adjustments(self, parent):
        sliders = [
            ("Brillo", -100, 100, 0, 1, "%.0f"),
            ("Contraste", -100, 100, 0, 1, "%.0f"),
            ("Saturacion", -100, 100, 0, 1, "%.0f"),
            ("Tono", -100, 100, 0, 1, "%.0f"),
            ("Nitidez", -100, 100, 0, 1, "%.0f"),
            ("Gamma", 10, 300, 100, 1, "%.2f"),
            ("Temperatura", -100, 100, 0, 1, "%.0f"),
            ("Vibrancia", -100, 100, 0, 1, "%.0f"),
            ("Exposicion", -100, 100, 0, 1, "%.0f"),
        ]
        keys = ["brightness", "contrast", "saturation", "hue", "sharpness",
                "gamma", "temperature", "vibrance", "exposure"]

        for (label, from_, to, initial, res, fmt), key in zip(sliders, keys):
            eng_val = self._engine.adjustments.get(key, 0)
            if key == "gamma":
                eng_val = self._engine.adjustments.get(key, 1.0) * 100
            s = AdjustmentSlider(
                parent, label, from_, to,
                eng_val,
                res, fmt,
                on_change=lambda v, k=key: self._on_adj_changed(k, v)
            )
            s.pack(fill=tk.X)
            self._adj_sliders[key] = s

    def _on_adj_changed(self, key: str, value: float):
        if key == "gamma":
            value = value / 100.0
        self._engine.set_adjustment(key, value)
        self._schedule_render()

    def _reset_adjustments(self):
        self._engine.reset_adjustments()
        for key, slider in self._adj_sliders.items():
            default = 0
            if key == "gamma":
                default = 100
            slider.set_value(default)
        self._schedule_render()
        self._update_status("Ajustes restablecidos")

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
            self._schedule_render()

    def _show_colors(self, style_info: dict):
        for widget in self._colors_container.winfo_children():
            widget.destroy()
        self._color_rows.clear()
        for key, color in style_info["colors"].items():
            label = f"  {key.capitalize()}"
            row = ColorRow(
                self._colors_container, label, color,
                on_change=lambda c, k=key: self._on_color_changed(k, c)
            )
            row.pack(fill=tk.X, pady=1)
            self._color_rows[key] = row

    def _on_color_changed(self, key: str, color: tuple[int, int, int]):
        self._engine.style_manager.update_style_color(self._engine.current_style_id, key, color)
        self._schedule_render()

    def _schedule_render(self):
        if self._render_after_id is not None:
            self.after_cancel(self._render_after_id)
        self._render_after_id = self.after(200, self._do_auto_render)

    def _do_auto_render(self):
        self._render_after_id = None
        if self._image_path:
            self._render()

    def _load_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("Todos", "*.*")]
        )
        if path:
            self._image_path = path
            self._update_status(f"Cargado: {os.path.basename(path)}")
            self._render()

    def _render(self):
        if self._image_path:
            self._on_render(self._image_path)

    def _save_image(self):
        if not hasattr(self, "_last_result") or self._last_result is None:
            messagebox.showwarning("Sin imagen", "No hay imagen para guardar.")
            return
        path = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos", "*.*")]
        )
        if path:
            self._last_result.save(path)
            self._update_status(f"Guardado: {os.path.basename(path)}")

    def _update_status(self, text: str):
        self._status_label.config(text=text)

    def _draw_theme_swatch(self):
        self._theme_swatch.delete("all")
        self._theme_swatch.create_rectangle(0, 0, 18, 18, fill=th.ACCENT, outline="")

    def _pick_accent(self):
        code = colorchooser.askcolor(th.ACCENT, title="Color de acento")
        if code and code[0]:
            r, g, b = int(code[0][0]), int(code[0][1]), int(code[0][2])
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self._update_accent(hex_color)

    def _update_accent(self, hex_color: str):
        th.ACCENT = hex_color
        self._draw_theme_swatch()
        self._update_status(f"Acento cambiado a {hex_color}")

    def set_result(self, image):
        self._last_result = image
        self._update_status("Renderizado completado")

    def load_image(self):
        self._load_image()

    def save_image(self):
        self._save_image()
