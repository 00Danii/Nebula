from PIL import ImageDraw
from utils.font_utils import FontManager


class GridRenderer:
    def __init__(self):
        self._font_manager = FontManager()
        self._font_path: str | None = None
        self.font_size_main: int = 14
        self.font_size_small: int = 11
        self.num_lines: int = 10
        self.line_width: int = 1
        self.show_on_image: bool = False

    @property
    def font_path(self) -> str | None:
        return self._font_path

    @font_path.setter
    def font_path(self, path: str | None):
        self._font_path = path
        self._font_manager.clear_cache()

    def render(
        self,
        draw: ImageDraw.ImageDraw,
        width: int,
        height: int,
        grid_color,
        text_color,
        image_rect: tuple[int, int, int, int] | None = None,
    ):
        font_main = self._font_manager.load(self._font_path, self.font_size_main)
        font_small = self._font_manager.load(self._font_path, self.font_size_small)

        if image_rect:
            ix, iy, iw, ih = image_rect
            self._draw_margin_ticks(draw, ix, iy, iw, ih, grid_color, font_small, self.num_lines)
            self._draw_axes(draw, ix, iy, iw, ih, text_color, font_main, font_small)
            self._draw_cardinal_points(draw, ix, iy, iw, ih, text_color, font_main)
        else:
            self._draw_full_grid(draw, width, height, grid_color, self.num_lines)
            self._draw_axes_fallback(draw, width, height, text_color, font_main, font_small)
            self._draw_cardinal_points_fallback(draw, width, height, text_color, font_main)

    def _draw_full_grid(self, draw, width, height, color, num_lines):
        spacing_w = width / num_lines
        spacing_h = height / num_lines
        lw = self.line_width
        for i in range(1, num_lines):
            x = i * spacing_w
            draw.line([(x, 0), (x, height)], fill=color, width=lw)
            y = i * spacing_h
            draw.line([(0, y), (width, y)], fill=color, width=lw)

    def _draw_margin_ticks(self, draw, ix, iy, iw, ih, color, font, num_lines):
        step_x = iw / num_lines
        step_y = ih / num_lines
        tick_len = 6
        lw = self.line_width

        for i in range(1, num_lines):
            tx = ix + i * step_x
            ty = iy + i * step_y

            if self.show_on_image:
                draw.line([(tx, iy - tick_len), (tx, iy + ih)], fill=color, width=lw)
                draw.line([(tx, iy + ih), (tx, iy + ih + tick_len)], fill=color, width=lw)
                draw.line([(ix - tick_len, ty), (ix + iw, ty)], fill=color, width=lw)
                draw.line([(ix + iw, ty), (ix + iw + tick_len, ty)], fill=color, width=lw)
            else:
                draw.line([(tx, iy - tick_len), (tx, iy)], fill=color, width=lw)
                draw.line([(tx, iy + ih), (tx, iy + ih + tick_len)], fill=color, width=lw)
                draw.line([(ix - tick_len, ty), (ix, ty)], fill=color, width=lw)
                draw.line([(ix + iw, ty), (ix + iw + tick_len, ty)], fill=color, width=lw)

    def _draw_axes(self, draw, ix, iy, iw, ih, color, font_main, font_small):
        for val in (-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0):
            x_pos = ix + (val + 2.0) * (iw / 4.0)
            draw.text((x_pos - 10, iy + ih + 4), f"{val:.1f}", fill=color, font=font_small)
            y_pos = iy + (2.0 - val) * (ih / 4.0)
            draw.text((ix - 42, y_pos - 8), f"{val:.1f}", fill=color, font=font_small)

        draw.text((ix + iw // 2 - 55, iy + ih + 22), "X, unidad de R_p", fill=color, font=font_main)
        draw.text((ix - 68, iy + ih // 2 - 8), "Y, unidad de R_p", fill=color, font=font_main)

    def _draw_axes_fallback(self, draw, width, height, color, font_main, font_small):
        center_w = width / 2
        center_h = height / 2
        for val in (-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0):
            x_pos = (val + 2.0) * (width / 4.0)
            draw.text((x_pos - 10, height - 25), f"{val:.1f}", fill=color, font=font_small)
            y_pos = (2.0 - val) * (height / 4.0)
            draw.text((10, y_pos - 10), f"{val:.1f}", fill=color, font=font_small)
        draw.text((center_w - 60, height - 40), "X, unidad de R_p", fill=color, font=font_main)
        draw.text((10, center_h - 10), "Y, unidad de R_p", fill=color, font=font_main)

    def _draw_cardinal_points(self, draw, ix, iy, iw, ih, color, font):
        cx, cy = ix + iw // 2, iy + ih // 2
        offset = 16
        points = {
            "N": (cx - 5, iy - offset),
            "W": (ix - offset - 10, cy - 8),
            "S": (cx - 5, iy + ih + offset - 8),
            "E": (ix + iw + offset - 5, cy - 8),
        }
        for label, (x, y) in points.items():
            draw.text((x, y), label, fill=color, font=font)

    def _draw_cardinal_points_fallback(self, draw, width, height, color, font):
        cx, cy = width // 2, height // 2
        points = {"N": (cx - 5, 10), "W": (10, cy - 10), "S": (cx - 5, height - 25), "E": (width - 25, cy - 10)}
        for label, (x, y) in points.items():
            draw.text((x, y), label, fill=color, font=font)
