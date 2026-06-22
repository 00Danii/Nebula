from PIL import ImageDraw
from utils.font_utils import FontManager


class MetadataRenderer:
    def __init__(self):
        self._font_manager = FontManager()
        self._font_path: str | None = None
        self.font_size_main: int = 16
        self.font_size_small: int = 12

    @property
    def font_path(self) -> str | None:
        return self._font_path

    @font_path.setter
    def font_path(self, path: str | None):
        self._font_path = path
        self._font_manager.clear_cache()

    def render(self, draw: ImageDraw.ImageDraw, width: int, height: int, data: dict, color):
        font_main = self._font_manager.load(self._font_path, self.font_size_main)
        font_small = self._font_manager.load(self._font_path, self.font_size_small)

        self._draw_pole(draw, data, color, font_main, font_small)
        self._draw_bottom_left(draw, height, data, color, font_main, font_small)
        self._draw_arcseconds(draw, width, height, data, color, font_main)

    def _draw_pole(self, draw, data, color, font_main, font_small):
        draw.text((20, 20), "Pole (ECJ2000):", fill=color, font=font_main)
        draw.text((20, 45), f"{data['pole']}", fill=color, font=font_small)

    def _draw_bottom_left(self, draw, height, data, color, font_main, font_small):
        y_offset = height - 130
        draw.text((20, y_offset), "SEP (w,\u03b4):", fill=color, font=font_main)
        draw.text((20, y_offset + 22), f"{data['sep']}", fill=color, font=font_small)
        draw.text((20, y_offset + 52), "SSP (\u03bb,\u00df):", fill=color, font=font_main)
        draw.text((20, y_offset + 74), f"{data['ssp']}", fill=color, font=font_small)
        draw.text((20, y_offset + 98), "NP:", fill=color, font=font_main)
        draw.text((55, y_offset + 98), f"{data['np']}", fill=color, font=font_main)

    def _draw_arcseconds(self, draw, width, height, data, color, font_main):
        label = f"arcsecond: {data['arc']}"
        bbox = draw.textbbox((0, 0), label, font=font_main)
        tw = bbox[2] - bbox[0]
        draw.text((width - tw - 20, height - 40), label, fill=color, font=font_main)
