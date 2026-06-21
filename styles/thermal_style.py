from PIL import Image
import numpy as np
import cv2
from styles.base_style import BaseStyle


_thermal_cmap: np.ndarray | None = None


def _build_thermal_lut() -> np.ndarray:
    lut = np.zeros((256, 3), dtype=np.uint8)
    for i in range(256):
        n = i / 255.0
        if n < 0.25:
            r, g, b = 0, 0, n / 0.25
        elif n < 0.5:
            t = (n - 0.25) / 0.25
            r, g, b = 0, t, 1.0 - t
        elif n < 0.75:
            t = (n - 0.5) / 0.25
            r, g, b = t, 1.0 - t, 0
        else:
            t = (n - 0.75) / 0.25
            r, g, b = 1.0, 1.0 - t * 0.5, t * 0.5
        lut[i] = (int(r * 255), int(g * 255), int(b * 255))
    return lut


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
        self._blend: float = 1.0
        self._intensity: float = 1.0
        self._grain: float = 0.0
        self._vignette: float = 0.0

        self._cv_cmaps = {
            "inferno": cv2.COLORMAP_INFERNO,
            "plasma": cv2.COLORMAP_PLASMA,
            "viridis": cv2.COLORMAP_VIRIDIS,
            "jet": cv2.COLORMAP_JET,
        }

    def get_palette(self) -> dict:
        return self._palette

    def get_style_params(self) -> dict[str, dict]:
        return {
            "palette": {"label": "Paleta de color", "type": "choice", "options": ["thermal", "inferno", "plasma", "viridis", "jet"], "value": self._palette_mode},
            "intensity": {"label": "Intensidad", "type": "slider", "min": 0, "max": 100, "value": int(self._intensity * 100)},
            "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": int(self._blend * 100)},
            "grain": {"label": "Ruido sensor", "type": "slider", "min": 0, "max": 100, "value": int(self._grain)},
            "vignette": {"label": "Viñeta", "type": "slider", "min": 0, "max": 100, "value": int(self._vignette)},
        }

    def get_style_param_groups(self) -> list[dict]:
        return [
            {
                "title": "Mapa de calor",
                "params": {
                    "palette": {"label": "Paleta de color", "type": "choice", "options": ["thermal", "inferno", "plasma", "viridis", "jet"], "value": self._palette_mode},
                    "intensity": {"label": "Intensidad", "type": "slider", "min": 0, "max": 100, "value": int(self._intensity * 100)},
                    "blend": {"label": "Mezcla", "type": "slider", "min": 0, "max": 100, "value": int(self._blend * 100)},
                },
            },
            {
                "title": "Efectos visor",
                "params": {
                    "grain": {"label": "Ruido sensor", "type": "slider", "min": 0, "max": 100, "value": int(self._grain)},
                    "vignette": {"label": "Viñeta", "type": "slider", "min": 0, "max": 100, "value": int(self._vignette)},
                },
            },
        ]

    def update_style_param(self, name: str, value):
        if name == "palette":
            self._palette_mode = value
        elif name == "intensity":
            self._intensity = value / 100.0
        elif name == "blend":
            self._blend = value / 100.0
        elif name == "grain":
            self._grain = float(value)
        elif name == "vignette":
            self._vignette = float(value)

    def process_subject(self, image: Image.Image) -> Image.Image:
        gray = np.array(image.convert("L"), dtype=np.uint8)
        h, w = gray.shape

        if self._palette_mode == "thermal":
            global _thermal_cmap
            if _thermal_cmap is None:
                _thermal_cmap = _build_thermal_lut()
            thermal = _thermal_cmap[gray]
        else:
            cmap = self._cv_cmaps.get(self._palette_mode, cv2.COLORMAP_INFERNO)
            thermal = cv2.applyColorMap(gray, cmap)
            thermal = cv2.cvtColor(thermal, cv2.COLOR_BGR2RGB)

        if self._intensity < 1.0 or self._blend < 1.0:
            thermal_f = thermal.astype(np.float32)
            if self._intensity < 1.0:
                gray3 = np.stack([gray] * 3, axis=2).astype(np.float32)
                thermal_f = thermal_f * self._intensity + gray3 * (1.0 - self._intensity)
            if self._blend < 1.0:
                gray3 = np.stack([gray] * 3, axis=2).astype(np.float32)
                thermal_f = thermal_f * self._blend + gray3 * (1.0 - self._blend)
            thermal = np.clip(thermal_f, 0, 255).astype(np.uint8)

        result = thermal.astype(np.float32)

        if self._grain > 0:
            noise = np.random.randn(h, w, 3).astype(np.float32) * self._grain * 1.5
            result = np.clip(result + noise, 0, 255)

        if self._vignette > 0:
            strength = self._vignette / 100.0
            x = np.arange(w, dtype=np.float32)
            y = np.arange(h, dtype=np.float32)
            mx, my = np.meshgrid(x, y)
            nx = (mx - w / 2.0) / (w / 2.0)
            ny = (my - h / 2.0) / (h / 2.0)
            d = np.sqrt(nx * nx + ny * ny)
            vignette = np.clip(1.0 - d * strength * 0.7, 0, 1)
            result *= vignette[:, :, np.newaxis]

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
