from PIL import Image
import numpy as np
from styles.base_style import BaseStyle


class SepiaStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "sepia"

    @property
    def name(self) -> str:
        return "Análisis Sepia Desaturado y Polvoriento"

    def __init__(self):
        super().__init__()
        self._background_color = (0, 0, 0)
        self._palette = {
            "text": (198, 160, 120),
            "grid": (60, 60, 60),
            "accent": (140, 110, 80),
        }
        self._intensity: float = 1.0
        self._tone: tuple[int, int, int] = (198, 160, 120)

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "intensity": {"label": "Intensidad", "type": "slider", "min": 0, "max": 100, "value": int(self._intensity * 100)},
            "tone": {"label": "Tono sepia", "type": "color", "value": self._tone},
        }

    def update_style_param(self, name: str, value):
        if name == "intensity":
            self._intensity = value / 100.0
        elif name == "tone":
            self._tone = value

    def process_subject(self, image: Image.Image) -> Image.Image:
        img_array = np.array(image.convert("RGB"), dtype=np.float32)
        gray = np.mean(img_array, axis=2, keepdims=True)
        tone = np.array(self._tone, dtype=np.float32)
        sepia = gray * (tone / 255.0)
        result = img_array * (1 - self._intensity) + sepia * self._intensity
        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
