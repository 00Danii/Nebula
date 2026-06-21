import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

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
        arrow = "\u25bc" if self._expanded else "\u25b6"
        text = self._toggle_btn.cget("text")
        self._toggle_btn.config(text=f"{arrow} {text[1:].strip()}")
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

    def configure_bg(self, bg):
        for child in self.winfo_children():
            try:
                child.configure(bg=bg)
            except tk.TclError:
                pass
            for sub in child.winfo_children():
                try:
                    sub.configure(bg=bg)
                except tk.TclError:
                    pass


class DarkColorPicker(tk.Toplevel):
    FIELD_SIZE = 200
    HUE_W = 22
    HUE_H = 200
    SWATCH_W = 50
    SWATCH_H = 26
    PRESET_COLS = 8
    PRESET_SIZE = 18

    def __init__(self, parent, initial: tuple[int, int, int],
                 title="Seleccionar color"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=th.BG_DARK)
        self.resizable(False, False)
        self.transient(parent)

        self._result: tuple[int, int, int] | None = None

        r, g, b = initial
        self._h, self._s, self._v = self._rgb_to_hsv(r, g, b)
        self._color = initial

        self._preset_colors = [
            (0, 0, 0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
            (128, 0, 0), (255, 0, 0), (255, 128, 128), (255, 200, 200),
            (0, 128, 0), (0, 255, 0), (128, 255, 128), (200, 255, 200),
            (0, 0, 128), (0, 0, 255), (128, 128, 255), (200, 200, 255),
            (128, 128, 0), (255, 255, 0), (255, 255, 128), (255, 255, 200),
            (0, 128, 128), (0, 255, 255), (128, 255, 255), (200, 255, 255),
            (128, 0, 128), (255, 0, 255), (255, 128, 255), (255, 200, 255),
            (64, 64, 64), (128, 64, 0), (255, 128, 0), (255, 200, 100),
        ]
        self._build()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda e: self._cancel())

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")
        self.focus_set()
        self.grab_set()

    @staticmethod
    def _rgb_to_hsv(r, g, b):
        nr, ng, nb = r / 255.0, g / 255.0, b / 255.0
        mx = max(nr, ng, nb)
        mn = min(nr, ng, nb)
        d = mx - mn
        if d == 0:
            h = 0
        elif mx == nr:
            h = 60 * (((ng - nb) / d) % 6)
        elif mx == ng:
            h = 60 * (((nb - nr) / d) + 2)
        else:
            h = 60 * (((nr - ng) / d) + 4)
        if h < 0:
            h += 360
        s = 0 if mx == 0 else (d / mx) * 255
        v = mx * 255
        return h, s, v

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        s = s / 255.0
        v = v / 255.0
        hi = int(h / 60) % 6
        f = (h / 60) - int(h / 60)
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        if hi == 0:
            r, g, b = v, t, p
        elif hi == 1:
            r, g, b = q, v, p
        elif hi == 2:
            r, g, b = p, v, t
        elif hi == 3:
            r, g, b = p, q, v
        elif hi == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))

    def _update_from_hsv(self):
        self._color = self._hsv_to_rgb(self._h, self._s, self._v)
        self._var_r.set(self._color[0])
        self._var_g.set(self._color[1])
        self._var_b.set(self._color[2])
        self._hex_var.set(self._rgb_hex(self._color))
        self._draw_field()
        self._draw_hue_bar()
        self._draw_preview()

    def _update_from_rgb(self):
        r, g, b = self._var_r.get(), self._var_g.get(), self._var_b.get()
        self._color = (r, g, b)
        self._h, self._s, self._v = self._rgb_to_hsv(r, g, b)
        self._hex_var.set(self._rgb_hex(self._color))
        self._draw_field()
        self._draw_hue_bar()
        self._draw_preview()

    def _build(self):
        main = tk.Frame(self, bg=th.BG_DARK, padx=12, pady=12)
        main.pack(fill=tk.BOTH, expand=True)

        # --- Photoshop-style picker area ---
        picker_row = tk.Frame(main, bg=th.BG_DARK)
        picker_row.pack(fill=tk.X, pady=(0, 8))

        field_frame = tk.Frame(picker_row, bg=th.BORDER, bd=1, relief=tk.FLAT)
        field_frame.pack(side=tk.LEFT)
        self._field = tk.Canvas(field_frame, width=self.FIELD_SIZE, height=self.FIELD_SIZE,
                                bg=th.BG_DARK, highlightthickness=0, bd=0, cursor="crosshair")
        self._field.pack()
        self._field.bind("<Button-1>", self._on_field_click)
        self._field.bind("<B1-Motion>", self._on_field_drag)

        hue_frame = tk.Frame(picker_row, bg=th.BORDER, bd=1, relief=tk.FLAT)
        hue_frame.pack(side=tk.LEFT, padx=(6, 0))
        self._hue_bar = tk.Canvas(hue_frame, width=self.HUE_W, height=self.HUE_H,
                                  bg=th.BG_DARK, highlightthickness=0, bd=0, cursor="hand2")
        self._hue_bar.pack()
        self._hue_bar.bind("<Button-1>", self._on_hue_click)
        self._hue_bar.bind("<B1-Motion>", self._on_hue_drag)

        # --- Preview + HEX ---
        preview_frame = tk.Frame(main, bg=th.BG_DARK)
        preview_frame.pack(fill=tk.X, pady=(0, 6))

        self._old_preview = tk.Canvas(preview_frame, width=self.SWATCH_W, height=self.SWATCH_H,
                                      highlightthickness=1, highlightbackground=th.BORDER,
                                      bg=th.BG_DARK, bd=0)
        self._old_preview.pack(side=tk.LEFT, padx=(0, 4))

        self._new_preview = tk.Canvas(preview_frame, width=self.SWATCH_W, height=self.SWATCH_H,
                                      highlightthickness=1, highlightbackground=th.BORDER,
                                      bg=th.BG_DARK, bd=0)
        self._new_preview.pack(side=tk.LEFT, padx=(0, 8))

        self._hex_var = tk.StringVar(value=self._rgb_hex(self._color))
        hex_entry = tk.Entry(preview_frame, textvariable=self._hex_var,
                             font=(th.FONT_FAMILY, 10),
                             bg=th.BG_INPUT, fg=th.FG,
                             highlightthickness=1, highlightbackground=th.BORDER,
                             bd=0, relief=tk.FLAT, width=9)
        hex_entry.pack(side=tk.LEFT)
        hex_entry.bind("<Return>", self._on_hex_enter)
        hex_entry.bind("<FocusOut>", self._on_hex_enter)

        # --- RGB sliders ---
        slider_frame = tk.Frame(main, bg=th.BG_DARK)
        slider_frame.pack(fill=tk.X, pady=(0, 6))

        self._var_r = tk.IntVar(value=self._color[0])
        self._var_g = tk.IntVar(value=self._color[1])
        self._var_b = tk.IntVar(value=self._color[2])

        for name, var, color in [("R", self._var_r, "#ff4444"),
                                  ("G", self._var_g, "#44ff44"),
                                  ("B", self._var_b, "#4444ff")]:
            f = tk.Frame(slider_frame, bg=th.BG_DARK)
            f.pack(fill=tk.X, pady=1)
            lbl = tk.Label(f, text=name, font=(th.FONT_FAMILY, 9, "bold"),
                           bg=th.BG_DARK, fg=color, width=2)
            lbl.pack(side=tk.LEFT)
            s = tk.Scale(f, from_=0, to=255, orient=tk.HORIZONTAL,
                         variable=var, showvalue=True,
                         width=8, length=180,
                         bg=th.BG_DARK, fg=th.FG, troughcolor=th.SLIDER_TROUGH,
                         activebackground=th.ACCENT, highlightthickness=0,
                         bd=0, sliderrelief=tk.FLAT)
            s.pack(side=tk.LEFT, padx=(4, 0), fill=tk.X, expand=True)
            s.bind("<ButtonRelease-1>", lambda e: self._update_from_rgb())

        # --- Preset palette ---
        palette_frame = tk.Frame(main, bg=th.BG_DARK)
        palette_frame.pack(fill=tk.X, pady=(0, 8))

        for i, (r, g, b) in enumerate(self._preset_colors):
            row_i, col_i = divmod(i, self.PRESET_COLS)
            c = tk.Canvas(palette_frame, width=self.PRESET_SIZE, height=self.PRESET_SIZE,
                          highlightthickness=1, highlightbackground=th.BORDER,
                          bg=th.BG_DARK, bd=0)
            c.grid(row=row_i, column=col_i, padx=1, pady=1)
            hex_c = f"#{r:02x}{g:02x}{b:02x}"
            c.create_rectangle(0, 0, self.PRESET_SIZE, self.PRESET_SIZE, fill=hex_c, outline="")
            c.bind("<Button-1>", lambda e, cr=(r, g, b): self._select_preset(cr))

        # --- Buttons ---
        btn_frame = tk.Frame(main, bg=th.BG_DARK)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Aceptar", font=(th.FONT_FAMILY, 9),
                  bg=th.BTN_BG, fg=th.FG,
                  activebackground=th.BTN_HOVER, activeforeground=th.FG_BRIGHT,
                  relief=tk.FLAT, bd=0, padx=16, pady=4,
                  command=self._accept).pack(side=tk.RIGHT, padx=(4, 0))
        tk.Button(btn_frame, text="Cancelar", font=(th.FONT_FAMILY, 9),
                  bg=th.BTN_BG, fg=th.FG_DIM,
                  activebackground=th.BTN_HOVER, activeforeground=th.FG,
                  relief=tk.FLAT, bd=0, padx=16, pady=4,
                  command=self._cancel).pack(side=tk.RIGHT)

        # --- Initial draw ---
        self._draw_field()
        self._draw_hue_bar()
        self._draw_preview()

    def _make_field_image(self):
        w = h = self.FIELD_SIZE
        img = Image.new("RGB", (w, h))
        px = img.load()
        for y in range(h):
            val = 1.0 - y / h
            for x in range(w):
                sat = x / w
                r, g, b = self._hsv_to_rgb(self._h, sat * 255, val * 255)
                px[x, y] = (r, g, b)
        return ImageTk.PhotoImage(img)

    def _make_hue_image(self):
        bw, bh = self.HUE_W, self.HUE_H
        img = Image.new("RGB", (bw, bh))
        px = img.load()
        for y in range(bh):
            hue = (y / bh) * 360
            r, g, b = self._hsv_to_rgb(hue, 255, 255)
            for x in range(bw):
                px[x, y] = (r, g, b)
        return ImageTk.PhotoImage(img)

    def _draw_field(self):
        self._field_img = self._make_field_image()
        self._field.delete("all")
        self._field.create_image(0, 0, anchor="nw", image=self._field_img)
        w = h = self.FIELD_SIZE
        sx = int(self._s / 255 * w)
        sy = int((1 - self._v / 255) * h)
        self._field.create_oval(sx - 4, sy - 4, sx + 4, sy + 4,
                                outline="#ffffff", width=2)
        self._field.create_oval(sx - 3, sy - 3, sx + 3, sy + 3,
                                outline="#000000", width=1)

    def _draw_hue_bar(self):
        self._hue_img = self._make_hue_image()
        self._hue_bar.delete("all")
        self._hue_bar.create_image(0, 0, anchor="nw", image=self._hue_img)
        bw = self.HUE_W
        bh = self.HUE_H
        sy = int(self._h / 360 * bh)
        self._hue_bar.create_rectangle(0, sy - 2, bw, sy + 2,
                                       outline="#ffffff", width=2)

    def _draw_preview(self):
        old = self._color
        self._old_preview.delete("all")
        self._old_preview.create_rectangle(0, 0, self.SWATCH_W, self.SWATCH_H,
                                           fill=self._rgb_hex(old), outline="")
        self._new_preview.delete("all")
        self._new_preview.create_rectangle(0, 0, self.SWATCH_W, self.SWATCH_H,
                                           fill=self._rgb_hex(self._color), outline="")

    def _rgb_hex(self, color):
        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    def _on_field_click(self, event):
        self._s = max(0, min(255, event.x / self.FIELD_SIZE * 255))
        self._v = max(0, min(255, (1 - event.y / self.FIELD_SIZE) * 255))
        self._update_from_hsv()

    def _on_field_drag(self, event):
        self._s = max(0, min(255, event.x / self.FIELD_SIZE * 255))
        self._v = max(0, min(255, (1 - event.y / self.FIELD_SIZE) * 255))
        self._update_from_hsv()

    def _on_hue_click(self, event):
        self._h = max(0, min(360, event.y / self.HUE_H * 360))
        self._update_from_hsv()

    def _on_hue_drag(self, event):
        self._h = max(0, min(360, event.y / self.HUE_H * 360))
        self._update_from_hsv()

    def _select_preset(self, color):
        r, g, b = color
        self._color = (r, g, b)
        self._h, self._s, self._v = self._rgb_to_hsv(r, g, b)
        self._var_r.set(r)
        self._var_g.set(g)
        self._var_b.set(b)
        self._hex_var.set(self._rgb_hex(color))
        self._draw_field()
        self._draw_hue_bar()
        self._draw_preview()

    def _on_hex_enter(self, event=None):
        try:
            h = self._hex_var.get().lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            self._color = (r, g, b)
            self._h, self._s, self._v = self._rgb_to_hsv(r, g, b)
            self._var_r.set(r)
            self._var_g.set(g)
            self._var_b.set(b)
            self._draw_field()
            self._draw_hue_bar()
            self._draw_preview()
        except (ValueError, IndexError):
            self._hex_var.set(self._rgb_hex(self._color))

    def _accept(self):
        self._result = self._color
        self.destroy()

    def _cancel(self):
        self._result = None
        self.destroy()

    def get_result(self) -> tuple[int, int, int] | None:
        return self._result


class ColorRow(tk.Frame):
    def __init__(self, parent, label: str, initial: tuple[int, int, int],
                 on_change, show_rgb: bool = True, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, **kwargs)
        self._on_change = on_change
        self._color = initial

        lbl = tk.Label(self, text=label, font=(th.FONT_FAMILY, 9),
                       bg=th.BG_DARK, fg=th.FG, anchor="w", width=14)
        lbl.pack(side=tk.LEFT, padx=8)

        self._swatch = tk.Canvas(self, width=18, height=18,
                                 highlightthickness=1, highlightbackground=th.BORDER,
                                 bg=th.BG_DARK, bd=0, cursor="hand2")
        self._swatch.pack(side=tk.LEFT, padx=(0, 6))
        self._draw_swatch()
        self._swatch.bind("<Button-1>", lambda e: self._pick())

        self._var_r = tk.IntVar(value=initial[0])
        self._var_g = tk.IntVar(value=initial[1])
        self._var_b = tk.IntVar(value=initial[2])

        if show_rgb:
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
        picker = DarkColorPicker(self, self._color, title="Seleccionar color")
        self.wait_window(picker)
        result = picker.get_result()
        if result:
            self._color = result
            self._var_r.set(result[0])
            self._var_g.set(result[1])
            self._var_b.set(result[2])
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


class StyleParamSlider(tk.Frame):
    def __init__(self, parent, label: str, min_val: int, max_val: int,
                 initial: int, on_change, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, **kwargs)
        self._on_change = on_change

        row = tk.Frame(self, bg=th.BG_DARK)
        row.pack(fill=tk.X, padx=8, pady=1)

        lbl = tk.Label(row, text=label, font=(th.FONT_FAMILY, 9),
                       bg=th.BG_DARK, fg=th.FG, anchor="w", width=14)
        lbl.pack(side=tk.LEFT)

        self._var = tk.DoubleVar(value=initial)
        slider = tk.Scale(row, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                          variable=self._var, showvalue=True,
                          resolution=1,
                          width=10, length=140,
                          bg=th.BG_DARK, fg=th.FG, troughcolor=th.SLIDER_TROUGH,
                          activebackground=th.ACCENT, highlightthickness=0,
                          bd=0, sliderrelief=tk.FLAT)
        slider.pack(side=tk.LEFT, padx=(4, 4), expand=True, fill=tk.X)
        slider.bind("<ButtonRelease-1>", lambda e: self._notify())

    def _notify(self):
        self._on_change(int(self._var.get()))

    def set_value(self, value: int):
        self._var.set(value)


class StyleParamColor(tk.Frame):
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
                                 bg=th.BG_DARK, bd=0, cursor="hand2")
        self._swatch.pack(side=tk.LEFT, padx=4)
        self._draw_swatch()
        self._swatch.bind("<Button-1>", lambda e: self._pick())

    def _draw_swatch(self):
        self._swatch.delete("all")
        self._swatch.create_rectangle(0, 0, 18, 18, fill=self._rgb_hex(), outline="")

    def _rgb_hex(self) -> str:
        return f"#{self._color[0]:02x}{self._color[1]:02x}{self._color[2]:02x}"

    def _pick(self):
        picker = DarkColorPicker(self, self._color, title="Seleccionar color")
        self.wait_window(picker)
        result = picker.get_result()
        if result:
            self._color = result
            self._draw_swatch()
            self._on_change(self._color)

    def set_color(self, color: tuple[int, int, int]):
        self._color = color
        self._draw_swatch()


class StyleParamChoice(tk.Frame):
    def __init__(self, parent, label: str, options: list[str],
                 initial: str, on_change, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, **kwargs)
        self._on_change = on_change

        lbl = tk.Label(self, text=label, font=(th.FONT_FAMILY, 9),
                       bg=th.BG_DARK, fg=th.FG, anchor="w", width=14)
        lbl.pack(side=tk.LEFT, padx=8)

        self._var = tk.StringVar(value=initial)
        values = options
        combobox = DarkCombobox(self, values=values, initial=initial,
                                width=18, on_select=self._on_change)
        combobox.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)


class DarkCombobox(tk.Frame):
    def __init__(self, parent, values=None, initial="", width=25, on_select=None, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, **kwargs)
        self._values = values or []
        self._on_select = on_select
        self._popup_open = False

        self._entry = tk.Entry(self, font=(th.FONT_FAMILY, 10), state="readonly",
                               readonlybackground=th.BG_INPUT, fg=th.FG,
                               highlightthickness=1, highlightbackground=th.BORDER,
                               bd=0, relief=tk.FLAT, width=width)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry.configure(state="normal")
        self._entry.insert(0, initial)
        self._entry.configure(state="readonly")

        self._btn = tk.Button(self, text="\u25bc", font=(th.FONT_FAMILY, 8),
                              bg=th.BG_DARK, fg=th.FG,
                              activebackground=th.BG_LIGHT, activeforeground=th.FG_BRIGHT,
                              relief=tk.FLAT, bd=0, padx=6, pady=0,
                              command=self._toggle_popup)
        self._btn.pack(side=tk.RIGHT)

        self._popup = None

    def _toggle_popup(self):
        if self._popup_open:
            self._close_popup()
        else:
            self._open_popup()

    def _open_popup(self):
        if not self._values:
            return
        self._popup = tk.Toplevel(self)
        self._popup.overrideredirect(True)
        self._popup.configure(bg=th.BORDER)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self._popup.geometry(f"+{x}+{y}")

        list_frame = tk.Frame(self._popup, bg=th.BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = DarkScrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(list_frame, font=(th.FONT_FAMILY, 10),
                                   bg=th.BG_INPUT, fg=th.FG,
                                   selectbackground=th.BG_LIGHT,
                                   selectforeground=th.FG_BRIGHT,
                                   highlightthickness=0, bd=0,
                                   relief=tk.FLAT,
                                   yscrollcommand=scrollbar.set,
                                   activestyle="none",
                                   exportselection=False)
        self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.configure(command=self._listbox.yview)

        for val in self._values:
            self._listbox.insert(tk.END, val)

        current = self._entry.get()
        if current in self._values:
            idx = self._values.index(current)
            self._listbox.selection_set(idx)
            self._listbox.see(idx)

        self._listbox.bind("<ButtonRelease-1>", self._on_list_select)
        self._listbox.bind("<Double-Button-1>", self._on_list_select)
        self._listbox.bind("<Leave>", lambda e: self._schedule_close())
        self._listbox.bind("<Enter>", lambda e: self._cancel_close())

        self._popup.bind("<FocusOut>", lambda e: self._close_popup())
        self._popup.focus_set()

        self._popup_open = True

    def _schedule_close(self):
        self._close_id = self.after(200, self._close_popup)

    def _cancel_close(self):
        if hasattr(self, '_close_id'):
            self.after_cancel(self._close_id)

    def _on_list_select(self, event):
        sel = self._listbox.curselection()
        if sel:
            idx = sel[0]
            value = self._values[idx]
            self._entry.configure(state="normal")
            self._entry.delete(0, tk.END)
            self._entry.insert(0, value)
            self._entry.configure(state="readonly")
            if self._on_select:
                self._on_select(value)
        self._close_popup()

    def _close_popup(self):
        self._popup_open = False
        if self._popup:
            self._popup.destroy()
            self._popup = None

    def get(self) -> str:
        return self._entry.get()

    def set(self, value: str):
        self._entry.configure(state="normal")
        self._entry.delete(0, tk.END)
        self._entry.insert(0, value)
        self._entry.configure(state="readonly")

    def configure_values(self, values: list[str]):
        self._values = values

    def current(self) -> int:
        val = self._entry.get()
        if val in self._values:
            return self._values.index(val)
        return -1


class DarkScrollbar(tk.Frame):
    def __init__(self, parent, orient=tk.VERTICAL, **kwargs):
        super().__init__(parent, bg=th.BG_DARK, width=12, **kwargs)
        self._command = None
        self._fraction = 0.0
        self._thumb_size = 1.0
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_frac = 0.0
        self._hovered = False

        self._canvas = tk.Canvas(self, bg=th.BG_DARK, highlightthickness=0, bd=0, width=12)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Configure>", lambda e: self._redraw())
        self._canvas.bind("<Enter>", lambda e: self._on_enter())
        self._canvas.bind("<Leave>", lambda e: self._on_leave())

    def _thumb_bounds(self):
        h = self._canvas.winfo_height()
        if h < 1:
            h = 100
        thumb_h = max(18, h * self._thumb_size)
        max_y = h - thumb_h
        thumb_y = self._fraction * max_y
        return h, thumb_h, max_y, thumb_y, thumb_y + thumb_h

    def _redraw(self):
        self._canvas.delete("all")
        h = self._canvas.winfo_height()
        if h < 1:
            return
        w = self._canvas.winfo_width()
        if w < 1:
            w = 12
        cx = w // 2
        self._canvas.create_rectangle(cx - 4, 0, cx + 4, h,
                                      fill=th.SCROLLBAR_TROUGH, outline="")
        _, _, _, y0, y1 = self._thumb_bounds()
        fill = th.SCROLLBAR_THUMB_HOVER if self._hovered else th.SCROLLBAR_THUMB
        self._canvas.create_rectangle(cx - 4, y0, cx + 4, y1, fill=fill, outline="")

    def _on_enter(self):
        self._hovered = True
        self._redraw()

    def _on_leave(self):
        self._hovered = False
        self._redraw()

    def _on_press(self, event):
        h, thumb_h, max_y, y0, y1 = self._thumb_bounds()
        if y0 <= event.y <= y1:
            self._dragging = True
            self._drag_start_y = event.y
            self._drag_start_frac = self._fraction
        else:
            self._fraction = (event.y - thumb_h / 2) / h
            self._fraction = max(0.0, min(1.0, self._fraction))
            self._redraw()
            if self._command:
                self._command("moveto", self._fraction)

    def _on_drag(self, event):
        if not self._dragging:
            return
        _, _, max_y, _, _ = self._thumb_bounds()
        dy = event.y - self._drag_start_y
        if max_y > 0:
            self._fraction = self._drag_start_frac + dy / max_y
        self._fraction = max(0.0, min(1.0, self._fraction))
        self._redraw()
        if self._command:
            self._command("moveto", self._fraction)

    def _on_release(self, event):
        self._dragging = False

    def set(self, first, last):
        self._fraction = float(first)
        self._thumb_size = float(last) - float(first)
        self._redraw()

    def configure(self, **kwargs):
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        super().configure(**kwargs)

    def config(self, **kwargs):
        self.configure(**kwargs)


class ControlsPanel(tk.Frame):
    def __init__(self, parent, engine, on_render, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=th.BG_DARK, width=280)
        self.pack_propagate(False)
        self._engine = engine
        self._on_render = on_render
        self._color_rows: dict[str, ColorRow] = {}
        self._adj_sliders: dict[str, AdjustmentSlider] = {}
        self._style_param_widgets: dict[str, tk.Frame] = {}
        self._image_path: str | None = None
        self._render_after_id: int | None = None
        self._build()

    def _build(self):
        self._scrollbar = DarkScrollbar(self, orient=tk.VERTICAL)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = tk.Canvas(self, bg=th.BG_DARK, highlightthickness=0, bd=0,
                                 yscrollcommand=self._scrollbar.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.configure(command=self._canvas.yview)

        scroll_frame = tk.Frame(self._canvas, bg=th.BG_DARK)
        self._canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _on_frame_configure(event):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        def _on_canvas_configure(event):
            self._canvas.itemconfig(1, width=event.width)

        scroll_frame.bind("<Configure>", _on_frame_configure)
        self._canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

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

        self._style_menu = DarkCombobox(sc, width=25,
                                         on_select=self._on_style_changed)
        self._style_menu.pack(fill=tk.X, padx=8, pady=4)

        self._colors_container = tk.Frame(sc, bg=th.BG_DARK)
        self._colors_container.pack(fill=tk.X, padx=0, pady=(0, 2))

        self._params_container = tk.Frame(sc, bg=th.BG_DARK)
        self._params_container.pack(fill=tk.X, padx=0, pady=(0, 4))

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
        self._style_menu.configure_values(names)
        if names:
            current = self._engine.current_style_id
            idx = next((i for i, s in enumerate(styles) if s["id"] == current), 0)
            self._style_menu.set(names[idx])
            self._show_style(styles[idx])

    def _on_style_changed(self, selected):
        styles = self._engine.list_styles()
        style_info = next((s for s in styles if s["name"] == selected), None)
        if style_info:
            self._engine.set_style(style_info["id"])
            self._show_style(style_info)
            self._schedule_render()

    def _show_style(self, style_info: dict):
        for widget in self._colors_container.winfo_children():
            widget.destroy()
        self._color_rows.clear()
        for key, color in style_info["colors"].items():
            label = f"  {key.capitalize()}"
            show_rgb = key not in ("text", "grid", "accent")
            row = ColorRow(
                self._colors_container, label, color,
                show_rgb=show_rgb,
                on_change=lambda c, k=key: self._on_color_changed(k, c)
            )
            row.pack(fill=tk.X, pady=1)
            self._color_rows[key] = row

        for widget in self._params_container.winfo_children():
            widget.destroy()
        self._style_param_widgets.clear()

        groups = style_info.get("param_groups")
        params = style_info.get("params", {})

        if groups:
            for gidx, group in enumerate(groups):
                if gidx > 0:
                    sep = tk.Frame(self._params_container, height=1, bg=th.BORDER)
                    sep.pack(fill=tk.X, padx=8, pady=3)
                gh = tk.Label(self._params_container, text=group["title"],
                              font=(th.FONT_FAMILY, 9, "bold"),
                              bg=th.BG_DARK, fg=th.FG_BRIGHT, anchor="w", padx=8)
                gh.pack(fill=tk.X, pady=(2, 0))
                for pname, pdef in group["params"].items():
                    self._build_param_widget(pname, pdef)
        elif params:
            sep = tk.Frame(self._params_container, height=1, bg=th.BORDER)
            sep.pack(fill=tk.X, padx=8, pady=2)
            for pname, pdef in params.items():
                self._build_param_widget(pname, pdef)

    def _build_param_widget(self, pname: str, pdef: dict):
        ptype = pdef.get("type")
        plabel = pdef.get("label", pname)
        if ptype == "slider":
            w = StyleParamSlider(
                self._params_container, plabel,
                pdef.get("min", 0), pdef.get("max", 100),
                pdef.get("value", 50),
                on_change=lambda v, n=pname: self._on_style_param_changed(n, v)
            )
            w.pack(fill=tk.X)
            self._style_param_widgets[pname] = w
        elif ptype == "color":
            w = StyleParamColor(
                self._params_container, plabel,
                pdef.get("value", (255, 255, 255)),
                on_change=lambda c, n=pname: self._on_style_param_changed(n, c)
            )
            w.pack(fill=tk.X, pady=1)
            self._style_param_widgets[pname] = w
        elif ptype == "choice":
            w = StyleParamChoice(
                self._params_container, plabel,
                pdef.get("options", []),
                pdef.get("value", ""),
                on_change=lambda v, n=pname: self._on_style_param_changed(n, v)
            )
            w.pack(fill=tk.X, pady=1)
            self._style_param_widgets[pname] = w

    def _on_color_changed(self, key: str, color: tuple[int, int, int]):
        self._engine.style_manager.update_style_color(self._engine.current_style_id, key, color)
        self._schedule_render()

    def _on_style_param_changed(self, name: str, value):
        self._engine.update_style_param(name, value)
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

    def set_result(self, image):
        self._last_result = image
        self._update_status("Renderizado completado")

    def load_image(self):
        self._load_image()

    def save_image(self):
        self._save_image()
