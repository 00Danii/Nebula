from PIL import Image, ImageDraw
from utils.font_utils import FontManager


class GridRenderer:
    def __init__(self):
        self._font_manager = FontManager()
        self._font_path: str | None = None
        self.font_size_main: int = 20
        self.font_size_small: int = 17
        self.num_lines: int = 8
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
        draw,
        width: int,
        height: int,
        grid_color,
        text_color,
        image_rect: tuple[int, int, int, int] | None = None,
        canvas: Image.Image | None = None,
    ):
        font_main = self._font_manager.load(self._font_path, self.font_size_main)
        font_small = self._font_manager.load(self._font_path, self.font_size_small)

        if image_rect:
            ix, iy, iw, ih = image_rect
            draw.rectangle([(ix, iy), (ix + iw, iy + ih)], outline=grid_color, width=self.line_width)
            self._draw_margin_ticks(draw, ix, iy, iw, ih, grid_color, font_small, self.num_lines)
            self._draw_axes(draw, ix, iy, iw, ih, text_color, font_main, font_small, canvas)
            self._draw_cardinal_points(draw, ix, iy, iw, ih, text_color, font_main)

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

    def _draw_axes(self, draw, ix, iy, iw, ih, color, font_main, font_small, canvas=None):
        for val in (-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0):
            x_pos = ix + (val + 2.0) * (iw / 4.0)
            if val != 0.0:
                draw.text((x_pos - 10, iy + ih + 14), f"{val:.1f}", fill=color, font=font_small)
                draw.text((x_pos - 10, iy - 26), f"{val:.1f}", fill=color, font=font_small)
            y_pos = iy + (2.0 - val) * (ih / 4.0)
            if val != 0.0:
                draw.text((ix - 46, y_pos - 8), f"{val:.1f}", fill=color, font=font_small)
                draw.text((ix + iw + 14, y_pos - 8), f"{val:.1f}", fill=color, font=font_small)

        draw.text((ix + iw // 2 - 55, iy + ih + 40), "X (unité de R_p)", fill=color, font=font_main)

        if canvas is not None:
            temp = Image.new("RGBA", (200, 30), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp)
            temp_draw.text((0, 0), "Y (unité de R_p)", fill=color, font=font_main)
            rotated = temp.rotate(90, expand=True)
            canvas.paste(rotated, (ix - 72, iy + ih // 2 - rotated.height // 2), rotated)


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
