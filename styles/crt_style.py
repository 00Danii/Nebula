from PIL import Image, ImageDraw
import numpy as np
from styles.base_style import BaseStyle


class CRTStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "crt"

    @property
    def name(self) -> str:
        return "Visualización CRT Analógica Retro"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (0, 255, 0),
            "grid": (0, 180, 0),
            "accent": (0, 255, 65),
        }
        self._scanline_intensity: float = 0.15
        self._phosphor_color: tuple[int, int, int] = (0, 255, 0)

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "scan_intensity": {"label": "Lineas de barrido", "type": "slider", "min": 0, "max": 100, "value": int(self._scanline_intensity * 100)},
            "phosphor": {"label": "Color de fosforo", "type": "color", "value": self._phosphor_color},
        }

    def update_style_param(self, name: str, value):
        if name == "scan_intensity":
            self._scanline_intensity = value / 100.0
        elif name == "phosphor":
            self._phosphor_color = value

    def process_subject(self, image: Image.Image) -> Image.Image:
        img_array = np.array(image.convert("L"), dtype=np.float32)
        normalized = img_array / 255.0
        phosphor = np.clip(normalized * 0.9 + 0.05, 0, 1)
        phosphor = np.power(phosphor, 1.0 / 2.2)
        pr, pg, pb = self._phosphor_color
        rgb = np.stack([
            np.clip(phosphor * pr / 255.0, 0, 1),
            np.clip(phosphor * pg / 255.0, 0, 1),
            np.clip(phosphor * pb / 255.0, 0, 1),
        ], axis=2)
        return Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8))

    def apply_post_effects(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, size: tuple[int, int]):
        w, h = size
        img_array = np.array(canvas, dtype=np.float32)
        scanlines = np.zeros((h, w, 3), dtype=np.float32)
        for y in range(0, h, 2):
            scanlines[y, :, :] = 1.0
        scanlines *= self._scanline_intensity
        img_array = img_array * (1.0 - scanlines)
        result = np.clip(img_array, 0, 255).astype(np.uint8)
        canvas.paste(Image.fromarray(result))
