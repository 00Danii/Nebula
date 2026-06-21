from PIL import Image
import numpy as np
from styles.base_style import BaseStyle


class NoirStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "noir"

    @property
    def name(self) -> str:
        return "Cine Noir"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (180, 180, 180),
            "grid": (70, 70, 70),
            "accent": (200, 200, 200),
        }

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        gray = np.array(image.convert("L"), dtype=np.float32)
        gray = np.clip((gray - 50) * 1.8 + 50, 0, 255)
        r = np.clip(gray * 0.92, 0, 255)
        g = np.clip(gray * 0.95, 0, 255)
        b = np.clip(gray * 1.0, 0, 255)
        return Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8))
