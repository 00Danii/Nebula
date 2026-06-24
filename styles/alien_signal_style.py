from PIL import Image, ImageDraw
import numpy as np
import cv2
from styles.base_style import BaseStyle


class AlienSignalStyle(BaseStyle):
    @property
    def id(self) -> str:
        return "alien_signal"

    @property
    def name(self) -> str:
        return "Transmisi\u00f3n Alien\u00edgena"

    def __init__(self):
        super().__init__()
        self._background_color = (8, 18, 30)
        self._palette = {
            "text": (0, 255, 190),
            "grid": (0, 200, 140),
            "accent": (255, 0, 180),
        }
        self._interference: int = 30
        self._chromatic: int = 40
        self._scan_intensity: int = 30
        self._alien_glow: int = 40
        self._color_drift: int = 50

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "interference": {"label": "Interferencia", "type": "slider", "min": 0, "max": 100, "value": self._interference},
            "chromatic": {"label": "Aberración cromática", "type": "slider", "min": 0, "max": 100, "value": self._chromatic},
            "scan_intensity": {"label": "Líneas de escaneo", "type": "slider", "min": 0, "max": 100, "value": self._scan_intensity},
            "alien_glow": {"label": "Resplandor alienígena", "type": "slider", "min": 0, "max": 100, "value": self._alien_glow},
            "color_drift": {"label": "Deriva de color", "type": "slider", "min": 0, "max": 100, "value": self._color_drift},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Señal",
                "params": {
                    "interference": {"label": "Interferencia", "type": "slider", "min": 0, "max": 100, "value": self._interference},
                    "chromatic": {"label": "Aberración cromática", "type": "slider", "min": 0, "max": 100, "value": self._chromatic},
                },
            },
            {
                "title": "Estilo visual",
                "params": {
                    "scan_intensity": {"label": "Líneas de escaneo", "type": "slider", "min": 0, "max": 100, "value": self._scan_intensity},
                    "alien_glow": {"label": "Resplandor alienígena", "type": "slider", "min": 0, "max": 100, "value": self._alien_glow},
                    "color_drift": {"label": "Deriva de color", "type": "slider", "min": 0, "max": 100, "value": self._color_drift},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "interference":
            self._interference = int(value)
        elif name == "chromatic":
            self._chromatic = int(value)
        elif name == "scan_intensity":
            self._scan_intensity = int(value)
        elif name == "alien_glow":
            self._alien_glow = int(value)
        elif name == "color_drift":
            self._color_drift = int(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        img_array = np.array(image.convert("RGB"), dtype=np.float32)
        h, w = img_array.shape[:2]

        drift = self._color_drift / 100.0
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]

        new_r = r * (1 - drift * 0.6) + g * drift * 0.3 + b * drift * 0.3
        new_g = r * drift * 0.15 + g * (1 - drift * 0.2) + b * drift * 0.05
        new_b = r * drift * 0.3 + g * drift * 0.15 + b * (1 - drift * 0.45)

        img_array = np.stack([new_r, new_g, new_b], axis=2)

        if self._chromatic > 0:
            shift = max(1, int(self._chromatic / 100.0 * 5))
            r_channel = np.roll(img_array[:,:,0], shift, axis=1)
            b_channel = np.roll(img_array[:,:,2], -shift, axis=1)
            mix = self._chromatic / 100.0
            img_array[:,:,0] = img_array[:,:,0] * (1 - mix) + r_channel * mix
            img_array[:,:,2] = img_array[:,:,2] * (1 - mix) + b_channel * mix

        if self._interference > 0:
            num_bands = int(self._interference * 0.4) + 1
            rng = np.random.default_rng()
            for _ in range(num_bands):
                y = rng.integers(0, max(1, h - 1))
                bh = rng.integers(2, 6)
                y_end = min(y + bh, h)
                actual_bh = y_end - y
                if actual_bh < 1:
                    continue
                band_strength = (self._interference / 100.0) * rng.uniform(0.2, 0.7)
                noise = rng.uniform(40, 215, (actual_bh, w, 3))
                img_array[y:y_end, :] = img_array[y:y_end, :] * (1 - band_strength) + noise * band_strength

        return Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

    def apply_post_effects(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, size: tuple[int, int]):
        img = np.array(canvas, dtype=np.float32)
        w, h = size

        if self._scan_intensity > 0:
            intensity = self._scan_intensity / 100.0
            step = max(2, int(30 * (1 - intensity * 0.9)))
            img[::step, :, :] *= 0.75

        if self._alien_glow > 0:
            glow = self._alien_glow / 100.0
            gray = np.mean(img, axis=2)
            bright_mask = gray > 180
            if np.any(bright_mask):
                bloom = np.zeros_like(img)
                bloom[:,:,1] = img[:,:,1] * bright_mask * 0.6
                bloom[:,:,0] = img[:,:,0] * bright_mask * 0.3
                ksize = max(3, int(min(h, w) * 0.04) | 1)
                bloom = cv2.GaussianBlur(bloom, (ksize, ksize), ksize * 0.4)
                img = np.clip(img + bloom * glow * 0.5, 0, 255)

        result = np.clip(img, 0, 255).astype(np.uint8)
        canvas.paste(Image.fromarray(result))
