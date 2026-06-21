from PIL import Image, ImageDraw
import numpy as np
import cv2
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
        self._curvature: float = 0.0
        self._bloom_intensity: float = 0.0
        self._bloom_threshold: float = 0.7

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "scan_intensity": {"label": "Lineas de barrido", "type": "slider", "min": 0, "max": 100, "value": int(self._scanline_intensity * 100)},
            "curvature": {"label": "Curvatura", "type": "slider", "min": 0, "max": 100, "value": int(self._curvature)},
            "bloom_intensity": {"label": "Bloom", "type": "slider", "min": 0, "max": 100, "value": int(self._bloom_intensity)},
            "bloom_threshold": {"label": "Umbral bloom", "type": "slider", "min": 0, "max": 100, "value": int(self._bloom_threshold * 100)},
            "phosphor": {"label": "Color de fosforo", "type": "color", "value": self._phosphor_color},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Efectos CRT",
                "params": {
                    "scan_intensity": {"label": "Lineas de barrido", "type": "slider", "min": 0, "max": 100, "value": int(self._scanline_intensity * 100)},
                    "curvature": {"label": "Curvatura", "type": "slider", "min": 0, "max": 100, "value": int(self._curvature)},
                    "bloom_intensity": {"label": "Bloom", "type": "slider", "min": 0, "max": 100, "value": int(self._bloom_intensity)},
                    "bloom_threshold": {"label": "Umbral bloom", "type": "slider", "min": 0, "max": 100, "value": int(self._bloom_threshold * 100)},
                },
            },
            {
                "title": "Color",
                "params": {
                    "phosphor": {"label": "Color de fosforo", "type": "color", "value": self._phosphor_color},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "scan_intensity":
            self._scanline_intensity = value / 100.0
        elif name == "curvature":
            self._curvature = float(value)
        elif name == "bloom_intensity":
            self._bloom_intensity = float(value)
        elif name == "bloom_threshold":
            self._bloom_threshold = value / 100.0
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

        if self._bloom_intensity > 0:
            img_array = self._apply_bloom(img_array)

        if self._scanline_intensity > 0:
            img_array = self._apply_scanlines(img_array, w, h)

        if self._curvature > 0:
            img_array = self._apply_curvature(img_array, w, h)

        result = np.clip(img_array, 0, 255).astype(np.uint8)
        canvas.paste(Image.fromarray(result))

    def _apply_bloom(self, img_array: np.ndarray) -> np.ndarray:
        intensity = self._bloom_intensity / 100.0
        threshold = self._bloom_threshold
        gray = np.mean(img_array, axis=2)
        mask = gray > (threshold * 255)
        if not np.any(mask):
            return img_array
        bloom = img_array * np.stack([mask] * 3, axis=2)
        ksize = max(3, int(min(img_array.shape[:2]) * 0.03) | 1)
        bloom = cv2.GaussianBlur(bloom, (ksize, ksize), ksize * 0.3)
        return np.clip(img_array + bloom * intensity * 0.5, 0, 255)

    def _apply_scanlines(self, img_array: np.ndarray, w: int, h: int) -> np.ndarray:
        mask = np.ones((h, w, 3), dtype=np.float32)
        intensity = self._scanline_intensity * 0.5
        for y in range(0, h, 3):
            mask[y, :, :] = 1.0 - intensity
        return img_array * mask

    def _apply_curvature(self, img_array: np.ndarray, w: int, h: int) -> np.ndarray:
        if self._curvature < 0.5:
            return img_array
        strength = (self._curvature / 100.0) * 0.25
        x = np.arange(w, dtype=np.float32)
        y = np.arange(h, dtype=np.float32)
        map_x, map_y = np.meshgrid(x, y)
        cx, cy = w / 2.0, h / 2.0
        nx = (map_x - cx) / cx
        ny = (map_y - cy) / cy
        r2 = nx * nx + ny * ny
        scale = 1.0 + strength * r2
        map_x = np.clip(nx * scale * cx + cx, 0, w - 1)
        map_y = np.clip(ny * scale * cy + cy, 0, h - 1)
        return cv2.remap(img_array, map_x, map_y, cv2.INTER_LINEAR)
