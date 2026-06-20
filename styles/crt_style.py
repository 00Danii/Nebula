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
        self.scanline_intensity: float = 0.15
        self.bloom_intensity: float = 0.1

    def get_palette(self) -> dict:
        return self._palette

    def process_subject(self, image: Image.Image) -> Image.Image:
        img_array = np.array(image.convert("L"), dtype=np.float32)
        normalized = img_array / 255.0
        green = np.clip(normalized * 0.9 + 0.05, 0, 1)
        phosphor = np.power(green, 1.0 / 2.2)
        phosphor_img = np.clip(phosphor * 255, 0, 255).astype(np.uint8)
        rgb = np.stack([np.zeros_like(phosphor_img), phosphor_img, np.zeros_like(phosphor_img)], axis=2)
        return Image.fromarray(rgb)

    def apply_post_effects(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, size: tuple[int, int]):
        w, h = size
        img_array = np.array(canvas, dtype=np.float32)
        scanlines = np.zeros((h, w, 3), dtype=np.float32)
        for y in range(0, h, 2):
            scanlines[y, :, :] = 1.0
        scanlines *= self.scanline_intensity
        img_array = img_array * (1.0 - scanlines)
        result = np.clip(img_array, 0, 255).astype(np.uint8)
        canvas.paste(Image.fromarray(result))
