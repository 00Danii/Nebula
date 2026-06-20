from PIL import Image
import numpy as np
from styles.base_style import BaseStyle


class ThermalStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "thermal"

    @property
    def name(self) -> str:
        return "Escáner de Visión Térmica o Espectral"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (0, 255, 255),
            "grid": (0, 200, 200),
            "accent": (100, 255, 255),
        }

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        gray = np.array(image.convert("L"), dtype=np.float32)
        normalized = gray / 255.0

        r = np.clip(4.0 * normalized - 1.0, 0.0, 1.0) * 2.0
        g = np.where(
            normalized < 0.5,
            np.clip(4.0 * normalized - 2.0, 0.0, 1.0) * 2.0,
            np.clip(-4.0 * normalized + 4.0, 0.0, 1.0),
        )
        b = np.where(
            normalized > 0.25,
            np.clip(-4.0 * normalized + 3.0, 0.0, 1.0) * 2.0,
            1.0,
        )

        thermal = np.stack([
            np.clip(r * 255, 0, 255),
            np.clip(g * 255, 0, 255),
            np.clip(b * 255, 0, 255),
        ], axis=2).astype(np.uint8)

        return Image.fromarray(thermal)
