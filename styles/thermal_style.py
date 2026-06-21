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
        self._palette_mode: str = "thermal"

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "palette": {"label": "Paleta de color", "type": "choice", "options": ["thermal", "inferno", "plasma", "viridis"], "value": self._palette_mode},
        }

    def update_style_param(self, name: str, value):
        if name == "palette":
            self._palette_mode = value

    def process_subject(self, image: Image.Image) -> Image.Image:
        gray = np.array(image.convert("L"), dtype=np.float32)
        normalized = gray / 255.0

        if self._palette_mode == "thermal":
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
        elif self._palette_mode == "inferno":
            r = np.clip(4.0 * normalized - 1.0, 0.0, 1.0) * 2.0
            g = np.clip(normalized * 3.0 - 0.5, 0.0, 1.0)
            b = np.clip(1.0 - 3.0 * normalized, 0.0, 1.0)
        elif self._palette_mode == "plasma":
            r = np.clip(4.0 * normalized - 0.5, 0.0, 1.0) * 1.5
            g = np.clip(1.0 - 2.0 * np.abs(normalized - 0.5), 0.0, 1.0)
            b = np.clip(1.0 - 3.0 * normalized, 0.0, 1.0)
        else:
            r = np.clip(normalized * 2.0, 0.0, 1.0)
            g = np.clip(normalized * 1.5 - 0.25, 0.0, 1.0)
            b = np.clip(2.0 - normalized * 2.0, 0.0, 1.0)

        thermal = np.stack([
            np.clip(r * 255, 0, 255),
            np.clip(g * 255, 0, 255),
            np.clip(b * 255, 0, 255),
        ], axis=2).astype(np.uint8)

        return Image.fromarray(thermal)
