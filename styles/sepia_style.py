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

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        img_array = np.array(image.convert("RGB"), dtype=np.float32)
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        result = img_array @ sepia_matrix.T
        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image.fromarray(result)
