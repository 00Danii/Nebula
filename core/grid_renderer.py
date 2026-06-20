from PIL import Image, ImageDraw
from utils.font_utils import FontManager


class GridRenderer:
    def __init__(self):
        self._font_manager = FontManager()
        self._font_path: str | None = None

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
        num_lines: int = 10,
    ):
        font_main = self._font_manager.load(self._font_path, 16)
        font_small = self._font_manager.load(self._font_path, 12)
        self._draw_grid_lines(draw, width, height, grid_color, num_lines)
        self._draw_axes(draw, width, height, text_color, font_main, font_small)
        self._draw_cardinal_points(draw, width, height, text_color, font_main)

    def _draw_grid_lines(self, draw, width, height, color, num_lines):
        spacing_w = width / num_lines
        spacing_h = height / num_lines
        for i in range(1, num_lines):
            x = i * spacing_w
            draw.line([(x, 0), (x, height)], fill=color, width=1)
            y = i * spacing_h
            draw.line([(0, y), (width, y)], fill=color, width=1)

    def _draw_axes(self, draw, width, height, color, font_main, font_small):
        center_w = width / 2
        center_h = height / 2
        for val in (-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0):
            x_pos = (val + 2.0) * (width / 4.0)
            draw.text((x_pos - 10, height - 25), f"{val:.1f}", fill=color, font=font_small)
            y_pos = (2.0 - val) * (height / 4.0)
            draw.text((10, y_pos - 10), f"{val:.1f}", fill=color, font=font_small)

        draw.text((center_w - 60, height - 40), "X, unidad de R_p", fill=color, font=font_main)
        draw.text((10, center_h - 10), "Y, unidad de R_p", fill=color, font=font_main)

    def _draw_cardinal_points(self, draw, width, height, color, font):
        cx, cy = width // 2, height // 2
        points = {"N": (cx - 5, 10), "W": (10, cy - 10), "S": (cx - 5, height - 25), "E": (width - 25, cy - 10)}
        for label, (x, y) in points.items():
            draw.text((x, y), label, fill=color, font=font)
