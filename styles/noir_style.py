from PIL import Image, ImageDraw
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
        self._contrast: int = 60
        self._brightness: int = 50
        self._tone: int = 50
        self._grain: int = 0
        self._vignette: int = 50

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "contrast": {"label": "Contraste", "type": "slider", "min": 0, "max": 100, "value": self._contrast},
            "brightness": {"label": "Brillo", "type": "slider", "min": 0, "max": 100, "value": self._brightness},
            "tone": {"label": "Tono", "type": "slider", "min": 0, "max": 100, "value": self._tone},
            "grain": {"label": "Grano", "type": "slider", "min": 0, "max": 100, "value": self._grain},
            "vignette": {"label": "Vi\u00f1eta", "type": "slider", "min": 0, "max": 100, "value": self._vignette},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Iluminacion",
                "params": {
                    "contrast": {"label": "Contraste", "type": "slider", "min": 0, "max": 100, "value": self._contrast},
                    "brightness": {"label": "Brillo", "type": "slider", "min": 0, "max": 100, "value": self._brightness},
                },
            },
            {
                "title": "Estilo",
                "params": {
                    "tone": {"label": "Tono", "type": "slider", "min": 0, "max": 100, "value": self._tone},
                    "grain": {"label": "Grano", "type": "slider", "min": 0, "max": 100, "value": self._grain},
                    "vignette": {"label": "Vi\u00f1eta", "type": "slider", "min": 0, "max": 100, "value": self._vignette},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "contrast":
            self._contrast = int(value)
        elif name == "brightness":
            self._brightness = int(value)
        elif name == "tone":
            self._tone = int(value)
        elif name == "grain":
            self._grain = int(value)
        elif name == "vignette":
            self._vignette = int(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        gray = np.array(image.convert("L"), dtype=np.float32)
        contrast = self._contrast / 100.0 * 1.5 + 0.5
        brightness = self._brightness / 100.0 * 1.2 + 0.4
        gray = np.clip((gray - 50 * (2.0 - contrast)) * contrast + 50 * brightness, 0, 255)

        tone = self._tone / 100.0
        tr = 0.92 * (1.0 - tone) + 1.05 * tone
        tg = 0.95 * (1.0 - tone) + 0.98 * tone
        tb = 1.00 * (1.0 - tone) + 0.88 * tone

        r = np.clip(gray * tr, 0, 255)
        g = np.clip(gray * tg, 0, 255)
        b = np.clip(gray * tb, 0, 255)
        result = np.stack([r, g, b], axis=2)

        if self._grain > 0:
            h, w = result.shape[:2]
            seed = np.random.randint(0, 1000)
            rng = np.random.RandomState(seed)
            noise = rng.randn(h, w, 1).astype(np.float32) * self._grain * 0.35
            result = np.clip(result + noise, 0, 255)

        if self._vignette > 0:
            h, w = result.shape[:2]
            strength = self._vignette / 100.0
            x = np.arange(w, dtype=np.float32)
            y = np.arange(h, dtype=np.float32)
            mx, my = np.meshgrid(x, y)
            nx = (mx - w / 2.0) / (w / 2.0)
            ny = (my - h / 2.0) / (h / 2.0)
            d = np.sqrt(nx * nx + ny * ny)
            v = np.clip(1.0 - d * strength * 0.8, 0, 1)
            result *= v[:, :, np.newaxis]

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
